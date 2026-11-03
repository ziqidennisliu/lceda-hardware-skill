---
name: lceda-hardware
description: Build and review hardware in JLCEDA/LCEDA Pro through its native MCP, from connection setup and component selection to pin-level schematics, SPICE validation, stackup, PCB placement, routing, and BOM delivery. Use for new or existing projects and read-only audits; stay within the authorized stage and do not automatically order boards or parts.
---

# LCEDA Hardware Workflow

Turn hardware requirements into verifiable schematics and PCB artifacts. Identify the current stage and authorization first, then read only the relevant references. Respond in the user's language.

## Start or resume

1. Read project instructions, `PROGRESS.md`, and the current design. Treat historical reports as dated evidence, not live state. Initialize Git if the hardware project is not tracked; preserve existing changes.
2. Discover `jlceda`, call `help` first, then `doctor` and `session.list`. Reuse a healthy connection instead of reinstalling it.
3. If tools or dependencies are missing, read [setup](references/setup.md). A request to install or prepare the environment authorizes necessary local installation and a missing MCP registration; do not ask again for each command.
4. Run from this skill's directory using an available Python 3.10+ interpreter:

   ```sh
   python3 scripts/bootstrap.py --project /absolute/project --apply --register-codex --with-simulation --install-conda
   ```

   Omit the last two options when only connecting. Without `--apply`, the command diagnoses and plans without writing configuration or installing dependencies. Supply `--eda-bin` if automatic discovery fails. The EDA application must already be installed by the user.
5. Registration does not prove connection. Verify the host MCP tools, bridge, target session, and document separately. A host refresh may be required; never restart or close the user's EDA windows automatically.

## Stages and evidence

| Stage | Work and outputs | Evidence required to advance |
|---|---|---|
| 0. Connection and baseline | Capabilities, target identity, exports, recovery point | Unambiguous project and document |
| 1. Requirements and architecture | Measurement definition, ranges, power, interfaces, reference-design differences | Critical targets resolved; assumptions visible |
| 2. Components and pin contract | MPNs, packages, supply status, every pin, control truth tables | Every physical pin connected or justified NC; library mapping checked |
| 3. Schematic implementation | Batched placement/wiring, actual netlist, geometry audit, ERC | Expected and actual connectivity agree; ambiguities resolved |
| 4. Calculation and simulation | OP, AC, transient, tolerances, abnormal conditions | Every intended channel/state covered; failed ranges excluded explicitly |
| 5. Packages and stackup | SCH-to-PCB sync, mechanics, copper and material layers | Pad mapping, layer order, thickness, and rules consistent |
| 6. Initial placement | Module adjacency, local loops, positions and mounting sides | Critical loops, clearances, and both-side views reviewed |
| 7. Routing and copper | Critical nets, controls/power, copper rebuild, connectivity/DRC | Actual filled copper, complete required connections, completed DRC |
| 8. Delivery | Version-bound reports, BOM, fabrication review, bench plan | Draft, routed, fabrication-reviewed, and measured states distinguished |

Read [schematics](references/schematic.md) for stages 1–3, [simulation](references/simulation.md) for stage 4, [PCB](references/pcb.md) for stages 5–7, and [acceptance and recovery](references/acceptance.md) for stage 8 or interrupted work.

## Confirm decisions, not individual clicks

Use the [confirmation matrix](references/confirmations.md). Present a concrete proposal with parameters, costs, and consequences before asking for a missing decision. Existing answers and authorization persist.

- A read-only request prohibits design writes, saving, changing layers, closing the project, and writing to live-synchronized project files.
- “Continue” or “finish the remaining steps” continues the authorized scope; it does not authorize unrelated topology/mechanical changes, purchasing, publication, or fabrication orders.
- Bundle unresolved tradeoffs where practical. Continue independent analysis while waiting for answers.
- A proposed stackup without a selected manufacturer or thickness remains a proposal. Routine traces and decoupling parts do not each require approval.

## Editing invariants

- Bind session, project, and document UUIDs explicitly. Re-read identity and baseline before each mutation batch. Merge concurrent user changes; never overwrite them with an old snapshot.
- Query the current official API schema before calling it. `invoke.ok=true` means the script ran, not that the intended operation succeeded. Check business results and actual readback.
- Do not edit `.eprj2` SQLite directly. `.eprj3` may synchronize disk changes into the editor: file writes count as design edits. Prefer official APIs; use file generation only with current format documentation and authorization.
- Export recovery artifacts and define expected differences before batching edits. Save only when authorized. Verify IDs, designators, pins, nets, and protected objects after each batch.
- A timeout does not mean rollback. Inspect the actual task/UI/object state before retrying. After one evidence-based corrective retry with no progress, preserve the error and report the blocker instead of replaying mutations.
- Examples in official documentation that close windows, stop servers, or overwrite projects are not automatic cleanup instructions.

## Tools and state

Read the [tool contracts](references/tools.md); the machine-readable inventory is `assets/tool-catalog.json`. Packaged CLI tools are not automatically registered MCP tools. Native MCP handles design operations. Read-only PCB export, per-layer SVG/HTML, physical stack diagrams, ngspice execution, and pin audits have executable entry points.

Use [project-state.example.json](assets/project-state.example.json) for authorization, stage, hashes, and evidence, and [connection-manifest.example.json](assets/connection-manifest.example.json) for the pin contract. Replace example values before acceptance checks.

`python3 scripts/audit_connections.py EXPECTED.json ACTUAL.json --output report.json` checks normalized pin inventories, NC, net names/membership, duplicates, merges, and splits. It does not parse proprietary EDA formats or replace geometry/ERC/DRC. Export adapters must include all actual pins, including unexpected ones.

Record each downloaded resource's source URL, license/access policy, local path, and version/hash in project `PROGRESS.md`. Never bundle private libraries, credentials, or restricted vendor models. Report what was implemented, what was verified, the tested domain, and remaining work. Simulation and empty error responses are not proof of hardware performance.

Read the [case study](references/watch-pad-case.md) and [sources/compatibility](references/sources.md) when background matters. The reference board's six layers, electrode topology, and parameter values are examples, not defaults for new projects.
