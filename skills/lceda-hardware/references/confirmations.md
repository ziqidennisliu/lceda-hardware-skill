# Confirmation matrix

Ask for missing design decisions, not routine clicks. Previous answers and authorizations remain valid. Analysis, backups, exports, authorized reversible edits, and routine repairs continue without repeated approval. Present concrete options before asking; do not merely ask whether to continue.

| Stage | Do first | Confirm only if unresolved | Then proceed continuously |
|---|---|---|---|
| 0. Connection | Discover environment, capability, registration, sessions | Ambiguous target; conflicting server replacement; EDA upgrade; login or window restoration | Authorized dependency setup, missing registration, read-only baseline |
| 1. Requirements | Read history/reference, identify paths and differences, propose ranges/budgets | Measurement target, accuracy/bandwidth, power, external/on-board MCU, dimensions, budget, assembly | Requirements, architecture, candidate comparison |
| 2. Selection | Check datasheets, libraries, supply; recommend main/alternate parts | Non-equivalent substitutions; major topology/supply change; hand-soldering limits | Routine passives within agreed specifications and complete pin contract |
| 3. Schematic | Back up, read objects, plan exact changes, find overlap/wrong nets | Planning-only scope versus actual edits; a fix changes function or interface | Batched placement/wiring, layout fixes, netlist/geometry/ERC, authorized save |
| 4. Simulation | Calculate and simulate agreed ranges; disclose models and failures | Unknown load that changes selection; reduced requirements or new topology after failure; paid models | Range/tolerance/switching checks, authorized tuning and revalidation |
| 5. Mechanics/stackup | Verify footprints, analyze reference, propose layer tradeoffs | Outline/hole/window intent, layer count/thickness/manufacturer, bottom clearance, connector orientation | PCB sync, logical and physical layer creation, rules and keepouts |
| 6. Placement | Adjacency plan, critical loops, two-sided draft/screenshots | Moving fixed electrodes/interfaces/holes, changing outline, unlocking protected objects | Routine pose optimization, silkscreen and clearance review |
| 7. Routing | Critical nets, power/ground, regular routing, fill, DRC, local repairs | Changing agreed manufacturing rules, blind/buried vias, major mechanical or circuit changes | Complete connections, repair violations, rebuild copper, authorized save |
| 8. Delivery | Versioned files, BOM, firmware contract, fabrication/bench review | Unrequested external upload/publication, purchases, fabrication orders, or messages | Deliver artifacts; act externally only when explicitly authorized |

If the user specifies 50 kHz first and then 20–100 kHz, do not ask again for those frequencies. Adding 5/10 kHz expands the test request, not automatically the validated accuracy/range. If two mechanical drafts are to be retained, preserve both until the final fabrication outline is resolved.

Record decisions with value, source/date, applicable stage, and validity. Make assumptions visible. Reversible drafts can use stated provisional assumptions; fabrication acceptance cannot treat them as confirmed constraints.
