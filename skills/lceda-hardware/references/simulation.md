# Calculation and simulation

## Define what is being verified

Distinguish hand calculations, linear numerical solvers, ngspice behavioral circuits, manufacturer macro-models, extracted parasitics, and bench measurements. Running a behavioral model in ngspice is not full device validation. Agreement between solvers using the same model only checks numerical consistency.

Each test records topology hash, frequency, load, state/gain, temperature/tolerances, excitation convention (peak/RMS/peak-to-peak), metric, threshold source, result, and limitations. Verify the model against the current actual netlist and component values first; an old model cannot validate a new revision.

## Test progression

1. **OP/DC:** rails, bias, DC returns in all states, switch terminals, amplifier common mode/output, and ADC per-pin ranges. Include reset, unselected/off, power loss, and leakage-polarity corners.
2. **AC:** full-chain transfer, amplitude/phase, impedance, loading, and applicable feedback/stability analysis. Test target/boundary frequencies and plausible interior worst cases. Programmable excitation is not proof of usable measurement bandwidth.
3. **Transient:** startup phase, actual channel/off/channel sequences, gain changes, load steps, long-off drift, peaks, saturation and recovery. Examine peaks as well as settling windows; a linear model does not prove real saturation recovery.
4. **Corners:** independent mismatch, resistor ratios, effective capacitance, leakage, rails, temperature, excitation, and combined high-load cases. Finite samples are not a manufacturing-wide guarantee.
5. **ADC/firmware:** acquisition RC/time, drive strength, common mode, reference disturbance, LSB, synchronization, and aliasing. A low analog frequency alone does not prove adequate acquisition.

Validate every channel and control state; testing the driver or H channel alone does not validate the V channel.

## Electrode coupling and shared sensing

Represent contact impedances, tissue paths, finite and asymmetric inputs, off-state switch capacitance/leakage, interconnect capacitance, and common mode separately. Freeze other variables when testing one mechanism.

Report intended and unwanted responses, such as relative tissue and contact perturbations and their ratio, with explicit perturbation sizes. Different fixtures/gains cannot establish isolation improvement by raw amplitude comparison.

Disconnecting an H sensing input can reduce that branch's loading but cannot remove the common body path or residual capacitive loading. Larger bias resistors trade lower loading against leakage-induced offsets and settling. Shared post-switch coupling can reduce components, but does not eliminate the off-state common-node DC-return requirement.

## Reproducible execution

Use the dedicated conda environment or the packaged `run_spice.py` wrapper:

```sh
conda run -p /project/.conda-envs/lceda-hardware ngspice -b -o run.log test.cir
```

Record model licenses and origins. Do not redistribute restricted vendor models. Preserve decks, logs, summaries, key waveforms, dependency locks, and input hashes. Missing output or parse failure is a failed check, not permission to substitute calculated numbers as simulated results.

Revalidate affected paths and system limits after circuit/parameter changes. Pure text/silkscreen changes do not need circuit simulation. Package changes affecting capacitance, power rating, or parasitics do require relevant checks.

Deliver a validated operating domain plus calibration, gain, and blanking requirements. Start physical tests with dummy loads. For body-contact research, assess actual excitation, supply/isolation, and experimental requirements; low voltage and simulation success alone do not establish safe human use.
