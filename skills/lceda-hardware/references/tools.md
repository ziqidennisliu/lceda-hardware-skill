# Packaged tools and invocation contracts

The tools generalize methods used in the original project. Project-specific routers, circuit models, hardcoded dimensions, layer IDs, and special pad corrections are not presented as universal tools.

## Inventory

| Tool | Provider/runtime | Input and output | Side effects and limits |
|---|---|---|---|
| setup | `scripts/bootstrap.py`, Python standard library, installed EDA | Project/program path to diagnostics, optional registration/environment | Read-only by default; `--apply` writes local setup, never design contents |
| eda-help/read/edit | Native `jlceda` MCP | Current schema to business results and readback | Bind identity and authorization before writes |
| pcb-snapshot | `eda_snapshot.py` + `export_pcb.js` | Session/project/PCB UUIDs to actual JSON snapshot | No open/save/close; rejects wrong targets or concurrent content changes |
| pin-audit | `audit_connections.py` | Complete independent expected/actual inventories to differences | Read-only inputs; not a geometric or component-spec audit |
| spice-run | `run_spice.py`, ngspice | Reviewed deck/executable to logs and result JSON | Local simulation; process completion is not circuit acceptance |
| pcb-view | `pcb_view.py`, Python standard library | Actual V4 snapshot to layer SVGs, HTML, stack diagram/report | Read-only offline review; unsupported geometry reported |
| native-render | Official editor/manufacturing APIs | Current document/view to real canvas or manufacturing export | Query current schema; UI view changes do not authorize design writes |
| native-erc-drc | `SCH_Drc` / `PCB_Drc` | Design plus parameters to complete response | Preserve raw response; timeout/null cannot pass |
| copper-rebuild | Supported native API or copper-manager UI | Target design to rebuilt actual copper | Authorized design mutation; verify actual POURED |
| reference-layout | Appropriate native/ODB/Gerber readers | Reference files to layer/side/net evidence | Format-specific; filenames alone do not establish layer order |
| geometry-review | Shapely/numpy in dedicated environment | Normalized copper/holes/keepouts to clearances/connectivity | Needs verified geometry; does not replace native DRC |
| bom-export | Native manufacturing API, Python csv/json | Actual parts/assembly flags to BOM and pin tables | Distinguish multi-unit, DNP, electrodes, and external modules |

`assets/tool-catalog.json` describes these interfaces. It does not grant permissions or automatically register extra MCP servers. Prefer available native MCP; the official CLI is a fallback for the same underlying capability.

## Read and visualize the current PCB

First discover tools, run help/doctor/session listing, and read target identity. Verify the current APIs for project/PCB identity, native source, components/pins, lines/vias, pours/filled copper, and regions. Then, from the skill directory:

```sh
python3 scripts/eda_snapshot.py --session SESSION --project-uuid PROJECT_UUID --pcb-uuid PCB_UUID --output /project/reports/pcb-current.json
python3 scripts/pcb_view.py /project/reports/pcb-current.json --output-dir /project/reports/pcb-current-view
```

Use actual identities, not historical IDs. `--eda-bin` is available for snapshot export. Output must be a new `.json`, never a native project/source file. MCP can execute the same fixed `export_pcb.js` with `{projectUuid, pcbUuid}`; decode the gzip result and validate JSON without printing base64 in the chat.

Open `index.html` to highlight networks and inspect layers; SVGs are independently zoomable. `stackup.svg` uses actual LAYER_PHYS z-order/material/thickness, with schematic-height bars. Missing physical records are warnings, not an invitation to invent a stack from layer names.

The adapter targets V4.1.78: ordinary PCB coordinates and material thickness use mil, POURED uses 10 mil. Cross-check known dimensions/native views before another version. Supported features include LINE, L/ARC paths, common RECT/ELLIPSE/OVAL pads, ordinary through vias, and actual positive fill. Through-hole pad holes are center markers, not drill dimensions. Negative planes, blind/buried vias, and unsupported paths/pads require native review.

All layers use a top projection and designators are review annotations, not actual silkscreen. Native views/Gerber remain authoritative for label orientation, precise pads, holes, contours, and manufacturing. Preserve snapshot timestamp and hash; historical data is not current state.

## Simulation

Bootstrap optionally prepares ngspice and numerical/plotting/geometry packages. Run a reviewed deck with:

```sh
python3 scripts/run_spice.py /project/simulation/model.cir --ngspice /project/.conda-envs/lceda-hardware/bin/ngspice --output-dir /project/simulation/run-001
```

On Windows, use the actual environment executable path. Review `.include` origins and `.control` shell/output commands first. The wrapper runs in the deck directory to preserve relative model references; it is not an isolation sandbox. Existing output directories are preserved.

Use `.print`, `.measure`, or reviewed `wrdata` exports and Python/matplotlib for waveforms and comparisons. Thresholds come from requirements/datasheets. There is no generic automatic circuit-pass button. Reused numerical models must match the current topology and states.

## Geometry and routing boundaries

The original project used 45-degree A*, Shapely copper geometry, union-find connectivity, layer rendering, and window exclusion checks. Its router hardcoded an AFE region, special hole dimensions, layer IDs, and electrode nets; it is not bundled.

Normalize actual units, curves, pad geometry, via spans, copper islands, and manufacturing/mechanical rules before building a router or independent clearance model. Reuse the algorithms, not old coordinates. Native autorouting also requires capability discovery, preservation of critical routes, and small-batch validation. Without a complete rule model, do not claim arbitrary-board automatic routing.

## Typical tool sequences

- Read-only review: connection → target binding → snapshot → layer/native view → netlist/DRC reads → report.
- Schematic edit: library/pin contract → backup → authorized changes → independent export → pin/geometry/ERC audits → simulation.
- PCB edit: live snapshot → mechanics/stack/placement plan → authorized changes → native copper rebuild → complete DRC → fresh snapshot/views → authorized save/readback.
- Delivery: input hashes → logs and limitations → BOM, assembly/firmware contract, fabrication and bench tasks.

If a required tool is missing, report its impact. Continue with supported standard-library/native alternatives where possible. Skill text alone is not evidence that a tool exists or has been installed.
