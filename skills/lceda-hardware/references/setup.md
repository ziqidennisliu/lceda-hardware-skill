# Installation, connection, and diagnosis

## Compatibility

The official JLCEDA CLI guide documents a built-in CLI/MCP in desktop Pro V4.1.60 and later. This is not a guarantee for every release. The exercised baseline is macOS with JLCEDA Pro V4.1.78, bridge `4.1.78.34f5b8d9`. The web editor does not provide this local bridge. Windows/Linux discovery branches exist but have not been validated against a live editor here.

The native server command is the installed EDA executable followed by `--mcp stdio`. macOS discovery includes the vendor's localized application bundle name; that filesystem name is intentionally not translated in code. The official Windows example is `C:\Program Files\lceda-pro\lceda-pro.exe`.

Use `--eda-bin` for other installations. Do not guess ports, install a similarly named npm bridge, or inspect activation data. The bootstrap does not install or upgrade EDA.

## Install the skill

Copy `skills/lceda-hardware` into a skill location supported by the host, or run its installer:

```sh
python3 skills/lceda-hardware/scripts/install_skill.py --apply
```

The default is `$CODEX_HOME/skills`, or `~/.codex/skills` if unset, matching the original tested host. Hosts using the current `.agents` convention can specify:

```sh
python3 skills/lceda-hardware/scripts/install_skill.py --destination ~/.agents/skills --apply
```

Install one copy in the location supported by the host. Different existing contents are preserved, not overwritten. Refresh the skill list or start a new chat if necessary; do not close EDA.

## Bootstrap contract

Python 3.10+ standard library is required to start. Reuse the host's Python or an existing conda interpreter. If no interpreter is available, obtain the host-supported runtime or report that prerequisite; do not claim zero-runtime installation.

- Without `--apply`: discover programs and query CLI help/doctor/sessions; no project, configuration, or environment writes.
- With `--apply`: initialize Git only if untracked, add local runtime/cache ignore entries, and record setup results. Do not commit automatically or change the EDA design.
- `--register-codex`: inspect `codex mcp list --json`; reuse an identical enabled `jlceda` configuration, add a missing entry with `codex mcp add`, and stop on conflicts. Keep any config backup in the user's configuration directory, not in project artifacts. Do not print credentials or unrelated server configuration.
- `--with-simulation`: create `<project>/.conda-envs/lceda-hardware` with Python, ngspice, numpy, matplotlib, and shapely from conda-forge, then run an RC AC smoke test. Record resolved packages, sources, licenses, and an explicit environment lock. Require at least 2 GiB free before a fresh environment download; this is a preflight threshold, not a guaranteed final footprint. Do not upgrade an existing environment implicitly.
- `--install-conda`: if conda is absent, resolve the official Miniforge release and platform installer, download its SHA256 file, verify it, and install into a project-local prefix. No `conda init`, global PATH modification, or project-package installation into base. A checksum from the same official origin checks integrity; it is not an independent signature.
- A specific ngspice `PackagesNotFoundError` triggers installation of the remaining packages followed by a pinned official ngspice 47 source build on macOS/Linux with an existing C compiler and make. Disable optional GUI/FFTW dependencies, preserve XSPICE, and install into the dedicated prefix. Missing compilers or unsupported Windows packages are explicit blockers, not permission to install a system toolchain silently.
- Record exact download, space, solver, or permission errors. Preserve completed steps. Do not substitute unknown mirrors or fabricated simulation results. A partial prefix is not a working environment.

Run long installations as observable background tool sessions and report progress. Do not launch duplicate installers while one remains active. Read-only design audits must not use `--apply`.

## Four separate checks

1. **Executable:** help advertises `--mcp`. A process launch failure may be a sandbox/permission problem, not an unsupported version. Preserve exit code and stderr.
2. **Host MCP:** `jlceda` tools are discoverable. A successful config write does not prove the host loaded them; a refresh may be needed.
3. **Bridge:** call `help` before `doctor`; check `connected`, `versionMatch`, and `resultChannel`. Depending on the interface, payloads may be under `data` or `value`. Outer `ok` alone is insufficient.
4. **Project:** list sessions, match path/title, and read project/document identity, type, UUID, and inventory. Ask if multiple candidates cannot be distinguished; never select the first session implicitly. Open the intended project only if opening is authorized, without creating a replacement.

After `help(doc.api)`, query specific classes/methods. Example for the tested schema:

```json
{"path":"doc.api","input":{"className":"DMT_Project","methodName":"getCurrentProjectInfo"}}
```

Resolve document APIs from the current `DMT_EditorControl` reference. Do not infer method names from old scripts or follow destructive example cleanup code.

## Failure handling

| Symptom | Response |
|---|---|
| Tools absent | Check registration, executable permission, and host refresh before adding anything |
| `connected=false` | Check editor windows; open the specified project only within authorization |
| `versionMatch=false` | Identify client/bridge versions; review compatibility before an EDA upgrade |
| Invoke timeout | Read task/object progress; avoid duplicate mutations |
| `noWindowsAvailable` | Continue MCP reads; request window restoration only for required native UI work |
| DRC missing/null | Report incomplete, never zero errors |
| Unicode corruption/truncation | Page/batch data or use escaped/compressed transport with hashes |

Connection tests do not save, stop, or close existing sessions.
