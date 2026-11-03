# State, recovery, and delivery

Maintain one current-state entry point naming the authoritative project, session/document, editor/schema version, connection revision, save time, and hashes. Freeze historical reports; do not treat an old passing result as current evidence.

## Each edit batch

1. **Baseline:** export native design/source, objects, netlist, BOM, poses/faces/packages, mechanics, layers, and rules. Capture unsaved state through supported exports; copying the previous disk file alone is insufficient.
2. **Change plan:** identify objects, expected prior/new values, protected fields, and recovery method. Verify fragile API behavior on a small batch first.
3. **Guard:** stop the batch on wrong identity, unexpected baseline changes, or concurrent edits. Re-read and merge instead of overwriting.
4. **Apply/read back:** record actual IDs, business responses, errors, and timeouts. Undo only this operation's changes; avoid full rollback over user work.
5. **Accept/save:** confirm only allowed differences, relevant geometry/netlist/ERC/DRC, then an authorized save and persisted readback.

## Completion levels

| Level | Evidence |
|---|---|
| Design proposal | Requirements, connectivity intent, unresolved decisions; no implementation claim |
| Schematic complete | Full pin contract, selection/power review, geometry/ERC, saved design evidence |
| Simulation passed in a domain | Model/design binding, test matrix, results, limitations, failed cases |
| Initial placement complete | Actual poses/faces, critical adjacency, clearances, both-side views; routing may remain |
| Initial connections complete | Rebuilt copper, required pads connected, complete DRC, protected conditions and saved views |
| Fabrication artifacts ready | Manufacturer stack/rules, mechanics, mask/electrode finish, Gerber/drill/assembly review |
| Hardware performance verified | Bench records, calibration/noise/stability/abnormal-state results; not simulation alone |

## Resume after interruption

Read the last valid state/PROGRESS entry and then inspect the real target. Verify timestamps/hashes. Do not replay historical migration scripts; continue from actual differences. Observe any in-flight routing/save/installation before launching another.

When blocked, preserve the exact error, completed steps, remaining steps, and condition needed to proceed. Missing results are not passes, and elapsed time does not confirm a pending decision.

## Delivery

Provide real artifacts appropriate to the stage: native files/backups, BOM, pin table, actual netlist, ERC/DRC, simulation inputs/logs/results, stack/placement/routing views, firmware interface contract, open issues, and bench plan. Do not fill an acceptance bundle with empty templates.

Distinguish physical PCB components, multi-unit symbols, soldered parts, copper electrodes, external MCU/modules, and DNP. Group procurement by full MPN/specification and separate per-board from spare quantities. Verify listing SKU, package, tolerance, rating, and pack size. Search/link collection does not authorize orders.

For external content record `{url, license_or_access_policy, local_path, version_or_sha256}`. For online-only references record no local copy plus the derived report path. Keep private libraries and activation/account data out of public packages.
