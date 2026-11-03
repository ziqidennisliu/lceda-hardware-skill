# Stackup, placement, and routing

## Schematic-to-PCB synchronization

Back up actual PCB state and protect user outlines, electrodes, holes, windows, locked parts, and good routes. After sync, compare physical components, MPNs, packages, every pad net, and NCs. Library replacement can change orientation, pin ordering, and UUIDs; counts alone are insufficient.

Check real component and land dimensions. Shrink packages only when ratings, effective capacitance, power, and assembly constraints allow it. Verify connectors/modules against actual pitch, pin 1, and height.

## Analyze the reference board

Read native PCB, BOM, Gerber, drill files, and layer-order information. Separate mounting sides, logical copper layers, physical materials, positive pours, and negative planes. Names such as MID1/G1 alone do not prove physical order. Transfer functions and loops, not coordinates from a different topology.

Choose layer count from area, return paths, routing/power complexity, cost, and manufacturer capability. Six layers do not increase component mounting area; normal components still mount on the two outer faces.

## Implement the stackup

Record physical order, editor layer ID, copper type/purpose, adjacent reference, dielectric/copper thickness, total thickness, manufacturing rules, and confirmation status. Physical L2 is not necessarily editor ID 2; in the tested board ID 2 means Bottom. Query current enums rather than hardcoding inner IDs.

Verify physical material records after enabling logical layers. If the API lacks physical stackup support, use the official native layer manager through observable UI, then export/read back. Do not patch the private database.

A positive `POUR` defines a boundary and net, not filled copper. Rebuild natively and inspect actual `POURED` contours, islands, and connectivity. One POURED object may contain disconnected islands. Interpret negative planes separately.

## Placement order

1. Anchor mechanical interfaces, electrodes, holes, windows, keepouts, and two-sided assembly envelopes. A rectangular FILL is not automatically a physical cutout.
2. Group by signal function and actual designators, not by component type.
3. Place local loops: input protection/coupling, amplifier, gain feedback, ADC, and decoupling beside the relevant pins. Keep clock sources near loads and sensitive feedback/RG paths short on one face where practical.
4. Position modules using sensitivity, current loops, and return planes. Bring controls into the digital side rather than across sensitive inputs.
5. Review bottom clearance and true top/flipped views. Test one label's parent transform and its own mirror setting before bulk changes; neither mirror=true nor mirror=false is universally correct.

## Routing order and geometry

- Route critical analog/feedback/RG/reference paths first, then clocks/electrodes, controls, power and ground. Reserve power/ground escapes before signal traces trap supply pads.
- Prefer consistent horizontal/vertical/45-degree routing or intentional arcs. Avoid unnecessary detours, stubs, sharp corners, and decorative matching. Electrical constraints take priority over appearance.
- P/N names alone do not justify 50/100-ohm differential rules. Apply controlled impedance and matching only when the real requirements warrant them.
- Connect actual disconnected copper groups, not merely pad-center pairs. Check width, clearance, drills, annuli, board edges, windows, and cross-layer projections.
- Separate high-impedance sensing from long parallel clocks/excitation. Use local copper exclusions based on parasitic targets without unnecessarily destroying reference planes. Review return paths at layer transitions.
- Keep raw and buffered references separate. Size supply paths for current/voltage drop; a pour's name does not prove it feeds its loads.
- Native autorouting may complete suitable residual nets with explicit allowed layers/nets and preserved routes. After a timeout, inspect the existing job before starting another.

## Acceptance

Rebuild copper, run complete native DRC, independently check connectivity/protected objects, render actual layers, save if authorized, and verify persisted artifacts. Independent connectivity needs via spans, plated pads, separate islands, and actual fill.

Current APIs may return booleans or nested error trees. Preserve arguments, type, and completion status. Timeout/null is not zero violations. Hiding airwires or crosses does not establish connectivity; identify their actual object/layer meaning.

The native API may split or deduplicate lines. Compare canonical copper geometry/connectivity rather than requiring planned segment counts to match returned IDs exactly.

Use actual readback for delivered views and label candidate plans explicitly. DRC clearance is only acceptance under current rules, not fabrication approval or proof of analog performance.
