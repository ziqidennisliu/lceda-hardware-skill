# Sources, compatibility, and distribution boundaries

Reviewed November 4, 2026. Documentation changes; prefer the installed client's current `help`, `doc.api`, and `doc.format`. This is an independent skill, not an official JLCEDA product. No third-party executable, restricted model, private library, or native user project is bundled.

| Source | Purpose | License/access and local treatment |
|---|---|---|
| https://prodocs.lceda.cn/cn/api/guide/cli.html | Native CLI/MCP, sessions, invocation, formats | Public vendor documentation; original summaries in setup/tools/PCB references, no page copy |
| https://prodocs.lceda.cn/cn/api/guide/ | Official API discovery | Same; no copied complete manual |
| https://prodocs.lceda.cn/cn/format/pcb/attr/ | Attribute and mirror semantics | Public vendor documentation; case-study lesson only |
| https://developers.openai.com/codex/mcp | Codex stdio registration | Public OpenAI documentation; official CLI used, no credentials copied |
| https://developers.openai.com/codex/skills | Skill discovery and locations | Public OpenAI documentation; use the location supported by the host |
| https://github.com/conda-forge/miniforge | Optional local conda bootstrap | BSD-3-Clause; bundled packages retain their licenses; download logic only |
| https://conda.anaconda.org/conda-forge/ | Simulation/geometry packages | Package-specific licenses; record resolved metadata at installation |
| https://ngspice.sourceforge.io/download.html | Official simulator source | Modified BSD and exceptions; see source COPYING |
| https://downloads.sourceforge.net/project/ngspice/ng-spice-rework/47/ngspice-47.tar.gz | Pinned source-build fallback | Same; URL and previously verified SHA256 only, no archive bundled |
| https://github.com/XuanyouLiu/EITWatch_Hardware | Reference hardware/PCB/BOM/Gerber | Reference project hardware license CERN-OHL-P-2.0; recheck relevant directory licenses before reuse; no source files bundled |

The workflow synthesizes the original project's requirements, decisions, progress, schematic geometry audits, shared-channel comparisons, simulation revisions, package migration, six-layer setup, label fixes, initial-routing acceptance, and procurement records. Earlier installation logs were incomplete, so the documented installation procedure comes from current configuration, official guidance, and read-only tests rather than reconstructed claims.

Referenced hardware, vendor documentation, models, binaries, and packages retain their respective licenses and restrictions.

## Validation boundary

- Live native MCP, doctor/session discovery, and target project reading: tested on macOS / JLCEDA Pro V4.1.78.
- Read-only bootstrap and existing registration reuse: tested; user MCP configuration was not rewritten.
- Pin-audit failure detection, installer conflict handling, read-only plans, disk preflight, and supported geometry: offline tests included.
- Live PCB export and layer/stack rendering: tested against the original board without distributing that snapshot.
- ngspice execution: exercised with an existing ngspice 47 installation on an analytical RC fixture.
- Fresh dependency installation: attempted but interrupted by insufficient disk space; a 2 GiB pre-download check was added. This is not a completed fresh-install validation.
- Fresh Miniforge installation, live Windows/Linux EDA, the new source-build helper end to end, restricted vendor models, and different EDA versions: not verified by the original validation.

Passing a tool test does not establish a circuit's correctness or manufacturability. Update this boundary as further evidence becomes available.
