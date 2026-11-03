# Requirements, selection, and complete connectivity

## Requirements and reference designs

Record inputs/outputs, range, frequencies, signal definition, power, noise/accuracy, sampling, connectors, programming access, size, assembly, and availability. For an existing project, classify changes as keep, modify, add, or remove.

Prefer the reference's native schematic/PCB, BOM, Gerber, and license. Papers and images explain intent but do not replace connectivity. Match functions, networks, and feedback loops rather than designators or visual similarity. Recheck reused circuits against the new supply, load, frequency, and packages.

For impedance projects, two-terminal readings include contact and tissue paths; four-terminal transfer readings still depend on finite input impedance, contact imbalance, and common mode. Without current measurement or calibrated excitation amplitude, ADC voltage is not a pure impedance measurement. Physiological or PPG-artifact interpretation requires experiments.

## Component selection

Record designator, quantity, full manufacturer part number, manufacturer, actual package and size convention, device/symbol/footprint origin, supplier code, critical specifications, datasheet evidence, and candidate status.

- **Power:** headroom, load/startup, stability versus effective capacitance, dissipation, default enable state.
- **Amplifier/INA:** input common-mode limits and output swing versus gain/supply, bias-current return, input capacitance/leakage, noise, bandwidth, and closed-loop stability. REF is not an arbitrary ground pin.
- **ADC:** differential range plus each pin's absolute/common-mode limits, reference drive, kickback, acquisition time, digital levels/tristate, clocks and sampling. Single-ended use of a differential ADC must follow its datasheet; do not generically ground the negative input.
- **Switch:** supply/signal range, Ron/Coff/Con/leakage, break-before-make, reset/off/power-off behavior, logic thresholds. Verify DC returns before and after coupling in every state.
- **Resistor:** power/voltage, tolerance/TCR, ratio matching, loading, and thermal noise. A larger package does not inherently give greater precision.
- **Capacitor:** dielectric, tolerance, voltage rating, effective capacitance across the actual terminals, frequency/temperature, and pair mismatch. Node-to-ground common mode is not dielectric DC bias.
- **MCU/module:** pin levels/defaults, SPI mode/timing, chip-select conflicts, power direction/backfeed, connector orientation/pitch/height. External modules belong in procurement without inflating on-board counts.

A library listing is not stock evidence. Timestamp supplier checks, and verify substitutions beyond nominal resistance/capacitance.

## Single pin contract

Use `assets/connection-manifest.example.json`. Every physical package pin appears exactly once, including justified NCs. Multi-unit symbols share one package: normalize by physical pin while retaining symbol-instance information separately.

Cover signal/feedback paths; every supply/reference/bias pin; both ends of all decoupling parts; gain/compensation/EXT_CAP/oscillator controls; digital buses and defaults; reset/programming/external interfaces; and datasheet-recommended handling of unused amplifiers, switch channels, and logic inputs.

Define control truth tables and startup order. Keep raw versus buffered references and host-side versus chip-side series-resistor nets distinct.

## Implementation and checking

Search official libraries, create instances, read back, then assign properties/designators and verify symbol-pin to footprint-pad mapping. Measure pin coordinates through the API; do not infer pitch from the symbol body. Check multi-unit, rotated, and mirrored instances independently.

Use small guarded batches, skip already completed objects, and update attached wires/labels when moving components. Moving text alone does not fix connectivity.

Three checks complement each other:

1. **Semantic:** compare the pin contract, independently exported netlist, and actual PCB pads. Include unexpected pins, NCs, merged nets, and split nets.
2. **Geometric:** detect coincident pins, pins on foreign nets, foreign wire endpoint contact, T-junctions, collinear overlap, and label anchors. Establish coordinate units/axis/tolerance. Intentional non-junction crossings follow editor semantics; they are not all shorts.
3. **Native/visual:** preserve ERC/DRC parameters, returned types, completion status, and actual renderings. An empty list is meaningful only after a completed, correctly interpreted check.

If foreign wires touch visually but the exported netlist remains separate, report the ambiguity precisely, fix it, and recheck. Do not claim either a confirmed power short or complete correctness.

Save within authorization and verify persisted artifacts/hashes. Freeze historical reports and update the active generator/manifest entry point so later runs cannot restore obsolete parts or nets.
