#!/usr/bin/env python3
"""Discover native JLCEDA MCP; optionally register and prepare isolated simulation tools."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request


class SetupError(RuntimeError):
    pass


def run(argv, timeout=60, cwd=None, env=None):
    try:
        p = subprocess.run([str(x) for x in argv], capture_output=True, text=True, timeout=timeout, cwd=cwd, env=env)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise SetupError(f"{argv[0]}: {type(e).__name__}: {e}") from e
    if p.returncode:
        raise SetupError(f"{argv[0]} exit={p.returncode}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p.stdout


def unwrap(raw):
    obj = json.loads(raw)
    if obj.get("ok") is not True:
        raise SetupError(json.dumps(obj, ensure_ascii=False))
    return obj.get("data", obj.get("value"))


def find_eda(explicit=None):
    candidates = [explicit] if explicit else []
    if not explicit:
        candidates += [shutil.which(x) for x in ("lceda-pro", "LCEDA-Pro")]
        candidates += ["/Applications/嘉立创EDA(专业版).app/Contents/MacOS/LCEDA-Pro",
                       str(Path.home()/"Applications/嘉立创EDA(专业版).app/Contents/MacOS/LCEDA-Pro")]
        for env in ("ProgramFiles", "LOCALAPPDATA"):
            if os.environ.get(env):
                candidates += [str(Path(os.environ[env])/"lceda-pro/lceda-pro.exe")]
    for value in candidates:
        if value and Path(value).expanduser().is_file():
            return Path(value).expanduser().resolve()
    raise SetupError("EDA executable not found. Supply --eda-bin for the installed desktop Pro client; no EDA was installed or upgraded.")


def probe(eda):
    help_text = run([eda, "--help"])
    if "--mcp" not in help_text:
        raise SetupError("Installed executable help does not advertise --mcp; verify official version support before changing registration")
    doctor = unwrap(run([eda, "doctor"]))
    sessions = unwrap(run([eda, "session", "list"]))
    return {"doctor": doctor, "sessions": sessions,
            "bridge_ready": all(doctor.get(k) is True for k in ("connected", "versionMatch", "resultChannel")),
            "host_tools_verified": False, "target_document_verified": False}


def registration_status(rows, eda):
    matches = [x for x in rows if x.get("name") == "jlceda"]
    if not matches:
        return "missing"
    if len(matches) != 1:
        raise SetupError("Multiple jlceda configurations found; preserve and review")
    item = matches[0]
    transport = item.get("transport", item)
    command = transport.get("command", "")
    if (Path(command).expanduser().resolve() == eda.resolve()
            and transport.get("args") == ["--mcp", "stdio"] and item.get("enabled", True)):
        return "reused"
    raise SetupError("Existing jlceda configuration differs or is disabled; preserved. Review its command/args before replacement.")


def register(eda, apply):
    codex = shutil.which("codex")
    if not codex:
        raise SetupError("codex CLI not found; configure native stdio in the host MCP settings using the discovered executable")
    rows = json.loads(run([codex, "mcp", "list", "--json"]))
    state = registration_status(rows, eda)
    if state == "missing" and apply:
        config = Path(os.environ.get("CODEX_HOME", str(Path.home()/".codex"))) / "config.toml"
        if config.exists():
            backup = config.with_name(f"config.toml.before-lceda-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}")
            shutil.copyfile(config, backup)
            backup.chmod(0o600)
        run([codex, "mcp", "add", "jlceda", "--", eda, "--mcp", "stdio"])
        if registration_status(json.loads(run([codex, "mcp", "list", "--json"])), eda) != "reused":
            raise SetupError("MCP registration readback failed")
        state = "registered; host MCP refresh may be needed"
    return state if state != "missing" else "would_register"


def find_conda(project):
    choices = [shutil.which("conda"), os.environ.get("CONDA_EXE"),
               str(project/".lceda-work/tools/miniforge/bin/conda"),
               str(project/".lceda-work/tools/miniforge/Scripts/conda.exe")]
    for root in (Path.home()/"miniforge3", Path.home()/"miniconda3", Path('/opt/anaconda3')):
        choices.append(str(root/"bin/conda"))
    return next((str(Path(x).resolve()) for x in choices if x and Path(x).is_file()), None)


def fetch(url):
    if not url.startswith("https://"):
        raise SetupError("Only HTTPS downloads supported")
    req = urllib.request.Request(url, headers={"User-Agent": "lceda-hardware-skill"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def append_progress(project, title, records):
    with (project/"PROGRESS.md").open("a", encoding="utf-8") as f:
        f.write(f"\n## {datetime.now(timezone.utc).isoformat()} — {title}\n\n")
        for r in records:
            f.write(f"- Source: {r['url']}; license/access: {r['policy']}; local path: `{r['local_path']}`; version/hash: {r.get('version_or_sha256', 'see record')}\n")


def install_conda(project):
    system, machine = platform.system(), platform.machine().lower()
    machine = {"amd64": "x86_64", "aarch64": "arm64" if system == "Darwin" else "aarch64"}.get(machine, machine)
    allowed = {("Darwin", "arm64"), ("Darwin", "x86_64"), ("Linux", "x86_64"), ("Linux", "aarch64"), ("Windows", "x86_64")}
    if (system, machine) not in allowed:
        raise SetupError(f"No automatic Miniforge recipe for {system}/{machine}")
    ext = "exe" if system == "Windows" else "sh"
    filename = f"Miniforge3-{system}-{machine}.{ext}"
    meta_url = "https://api.github.com/repos/conda-forge/miniforge/releases/latest"
    meta_bytes = fetch(meta_url)
    release = json.loads(meta_bytes)
    assets = {x["name"]: x["browser_download_url"] for x in release["assets"]}
    urls = [assets.get(filename), assets.get(filename + ".sha256")]
    if not all(urls) or not all(x.startswith("https://github.com/conda-forge/miniforge/releases/download/") for x in urls):
        raise SetupError(f"Official release lacks installer/checksum for {filename}")
    cache = project/".lceda-work/downloads"
    cache.mkdir(parents=True, exist_ok=True)
    metadata = cache/"miniforge-release.json"
    metadata.write_bytes(meta_bytes)
    records = [{"url": meta_url, "policy": "GitHub public API access terms; release metadata", "local_path": str(metadata), "version_or_sha256": sha(metadata)}]
    append_progress(project, "Miniforge release source", records)
    for url in urls:
        path = cache/url.rsplit("/", 1)[1]
        path.write_bytes(fetch(url))
        rec = {"url": url, "policy": "Miniforge BSD-3-Clause; bundled packages retain their own licenses", "local_path": str(path), "version_or_sha256": sha(path)}
        records.append(rec)
        append_progress(project, "Miniforge downloaded source", [rec])
    installer = cache/filename
    checksum = (cache/(filename + ".sha256")).read_text().split()[0]
    if not re.fullmatch(r"[a-fA-F0-9]{64}", checksum) or sha(installer) != checksum.lower():
        raise SetupError("Miniforge SHA256 mismatch; installer NOT executed")
    prefix = project/".lceda-work/tools/miniforge"
    if prefix.exists():
        raise SetupError(f"Partial Miniforge prefix preserved: {prefix}; inspect before retrying")
    if system == "Windows":
        run([installer, "/InstallationType=JustMe", "/RegisterPython=0", "/AddToPath=0", "/S", f"/D={prefix}"], 1200)
    else:
        run(["bash", installer, "-b", "-p", prefix], 1200)
    conda = find_conda(project)
    if not conda:
        raise SetupError("Miniforge installation finished but conda was not found")
    return conda


def build_ngspice(project, prefix):
    if platform.system() not in ("Darwin", "Linux"):
        raise SetupError("ngspice conda package unavailable; automatic source build only supports macOS/Linux with a C compiler. Windows needs a verified official binary or supported toolchain.")
    compiler, make = shutil.which("cc"), shutil.which("make")
    if not compiler or not make:
        raise SetupError("ngspice source build requires an installed C compiler and make; no system toolchain installed automatically")
    url = "https://downloads.sourceforge.net/project/ngspice/ng-spice-rework/47/ngspice-47.tar.gz"
    expected = "894e649651f1838a14095e5a5439e7d3aa63e87ede14d283173fda4fcdef675f"
    cache = project/".lceda-work/downloads"
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache/"ngspice-47.tar.gz"
    if not archive.exists():
        archive.write_bytes(fetch(url))
    append_progress(project, "ngspice official source", [{"url": url,
        "policy": "Modified BSD and exceptions including LGPL; retain archive COPYING",
        "local_path": str(archive), "version_or_sha256": sha(archive)}])
    if sha(archive) != expected:
        raise SetupError("ngspice pinned source SHA256 mismatch; archive not extracted or executed")
    root = project/".lceda-work/build"
    root.mkdir(exist_ok=True)
    source = root/"ngspice-47"
    if not source.exists():
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                dest = (root/member.name).resolve()
                if not dest.is_relative_to(root.resolve()) or not (member.isfile() or member.isdir()):
                    raise SetupError(f"Unsafe archive entry: {member.name}")
            tar.extractall(root)
    build = source/"release"
    build.mkdir(exist_ok=True)
    env = dict(os.environ, CC=compiler, CFLAGS="-O2 -fcommon -include stdlib.h")
    configure = [source/"configure", f"--prefix={prefix}", "--without-x", "--with-readline=no", "--with-editline=no",
                 "--with-fftw3=no", "--disable-openmp", "--enable-xspice", "--disable-osdi", "--disable-klu", "--disable-debug"]
    for label, argv in [("configure", configure), ("make", [make, "-j2"]), ("install", [make, "install"])]:
        print(f"ngspice source: {label}", flush=True)
        log = build/(label + ".log")
        try:
            log.write_text(run(argv, 1800, cwd=build, env=env))
        except SetupError as exc:
            log.write_text(str(exc))
            raise SetupError(f"ngspice {label} failed; see {log}") from exc
    append_progress(project, "ngspice source build", [{"url": url, "policy": "See source COPYING; no source modification",
        "local_path": str(prefix/"bin/ngspice"), "version_or_sha256": sha(prefix/"bin/ngspice")},
        {"url": url, "policy": "Extracted source and build logs; retain COPYING", "local_path": str(source), "version_or_sha256": expected}])


def simulation(project, apply, allow_conda):
    conda = find_conda(project)
    prefix = project/".conda-envs/lceda-hardware"
    if not apply:
        return {"conda": conda, "prefix": str(prefix), "action": "reuse or create isolated environment", "install_conda_if_missing": allow_conda}
    if not prefix.exists() and shutil.disk_usage(project).free < 2 * 1024**3:
        raise SetupError("Insufficient disk space for a fresh simulation environment: require at least 2 GiB free before downloads; no dependencies downloaded")
    if not conda:
        if not allow_conda:
            raise SetupError("conda missing; use --install-conda to authorize local Miniforge download")
        conda = install_conda(project)
    # Keep caches and environment registration out of the user's base environment.
    conda_env = dict(os.environ, CONDA_PKGS_DIRS=str(project/".lceda-work/conda-pkgs"), CONDA_REGISTER_ENVS="false")
    use_source = False
    if not prefix.exists():
        print("Creating isolated simulation environment; this may take several minutes", flush=True)
        append_progress(project, "Conda package/index access", [{"url": "https://conda.anaconda.org/conda-forge/",
            "policy": "Public conda-forge index; packages retain per-package licenses, recorded after install",
            "local_path": str(project/".lceda-work/conda-pkgs"), "version_or_sha256": "repository metadata/cache; resolved package versions recorded below"}])
        command = [conda, "create", "--yes", "--prefix", prefix, "--override-channels", "--channel", "conda-forge",
                   "python=3.11", "numpy", "matplotlib", "shapely"]
        try:
            run(command + ["ngspice"], 1800, env=conda_env)
        except SetupError as exc:
            if "PackagesNotFoundError" not in str(exc) or "ngspice" not in str(exc):
                raise
            (project/".lceda-work/ngspice-package-unavailable.log").write_text(str(exc))
            run(command, 1800, env=conda_env)
            use_source = True
    meta_dir = prefix/"conda-meta"
    if not meta_dir.is_dir():
        raise SetupError(f"Existing non-conda/partial prefix preserved: {prefix}")
    records = []
    for p in sorted(meta_dir.glob("*.json")):
        item = json.loads(p.read_text())
        records.append({"url": item.get("url") or item.get("channel") or "unknown; inspect conda metadata",
                        "policy": item.get("license") or "not stated; inspect package license before redistribution",
                        "local_path": str(p), "version_or_sha256": f"{item.get('name')} {item.get('version')} {item.get('build')}; sha256={item.get('sha256', 'not supplied')}"})
    append_progress(project, "Simulation dependency sources", records)
    work = project/".lceda-work"
    (work/"dependency-sources.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))
    (work/"conda-explicit.txt").write_text(run([conda, "list", "--prefix", prefix, "--explicit"], env=conda_env))
    if use_source:
        build_ngspice(project, prefix)
    run([conda, "run", "--prefix", prefix, "python", "-c", "import numpy,matplotlib,shapely; print('imports ok')"])
    # One independent numerical check: |1/(1+j*2*pi*1000*1000*1e-7)| = 0.846733...
    circuit = work/"bootstrap-rc.cir"
    circuit.write_text("RC bootstrap smoke\nV1 in 0 AC 1\nR1 in out 1k\nC1 out 0 100n\n.ac lin 1 1k 1k\n.print ac vm(out)\n.end\n")
    log = work/"bootstrap-ngspice.log"
    version = run([conda, "run", "--prefix", prefix, "ngspice", "--version"])
    run([conda, "run", "--prefix", prefix, "ngspice", "-b", "-o", log, circuit])
    values = re.findall(r"^\s*0\s+1\.0+e\+03\s+([\d.eE+\-]+)", log.read_text(), re.M)
    if not values or abs(float(values[-1]) - 0.84673301596) > 1e-5:
        raise SetupError(f"ngspice RC smoke missing/incorrect; inspect {log}")
    return {"prefix": str(prefix), "ngspice_version": version.strip(), "rc_smoke_passed": True,
            "scope": "toolchain only, not target circuit validation"}


def init_project(project):
    project.mkdir(parents=True, exist_ok=True)
    try:
        run(["git", "-C", project, "rev-parse", "--show-toplevel"])
    except SetupError:
        run(["git", "init", project])
    ignore = project/".gitignore"
    old = ignore.read_text() if ignore.exists() else ""
    additions = [x for x in (".conda-envs/", ".lceda-work/") if x not in old.splitlines()]
    if additions:
        with ignore.open("a") as f:
            f.write(("\n" if old and not old.endswith("\n") else "") + "\n".join(additions) + "\n")
    (project/".lceda-work").mkdir(exist_ok=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--eda-bin")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--register-codex", action="store_true")
    p.add_argument("--with-simulation", action="store_true")
    p.add_argument("--install-conda", action="store_true")
    a = p.parse_args()
    project = a.project.expanduser().resolve()
    result = {"schema_version": 1, "mode": "apply" if a.apply else "diagnostic", "project": str(project), "steps": {}}
    try:
        eda = find_eda(a.eda_bin)
        result["eda_executable"] = str(eda)
        result["steps"]["connection"] = probe(eda)
        if a.apply:
            init_project(project)
        if a.register_codex:
            result["steps"]["registration"] = register(eda, a.apply)
        if a.with_simulation:
            result["steps"]["simulation"] = simulation(project, a.apply, a.install_conda)
        result["setup_completed"] = True
        result["connection_fully_verified"] = False
        result["next"] = "Agent must discover host jlceda tools, help/doctor/session.list, then read and bind target project/document. Never choose the first session implicitly."
    except (SetupError, OSError, ValueError, KeyError) as e:
        result.update(setup_completed=False, error=f"{type(e).__name__}: {e}")
    if a.apply and (project/".lceda-work").is_dir():
        path = project/".lceda-work/bootstrap-result.json"
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        append_progress(project, "LCEDA bootstrap result", [{"url": "https://prodocs.lceda.cn/cn/api/guide/cli.html",
            "policy": "JLCEDA public documentation; installed client under its own license; no client download",
            "local_path": str(path), "version_or_sha256": sha(path)}])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("setup_completed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
