# LCEDA Hardware Skill

An agent skill and CLI toolkit for designing and reviewing hardware in JLCEDA Pro desktop.

## Workflow

1. Connect through native MCP and identify the active project and document.
2. Define requirements, select components, and capture every pin and net.
3. Build and check the schematic, then simulate critical circuits in ngspice.
4. Plan the physical stackup, place components, route the PCB, and review copper and DRC.
5. Deliver the BOM, design evidence, and remaining fabrication and bench checks.

The agent continues routine work within the authorized scope and asks about unresolved design decisions. See the [confirmation matrix](skills/lceda-hardware/references/confirmations.md).

## Included tools

| Tool | What it does |
| --- | --- |
| `bootstrap.py` | Discovers the native EDA bridge and optionally registers MCP and prepares an isolated simulation environment. |
| `eda_snapshot.py` | Exports the selected PCB to JSON after checking project and document identity. |
| `pcb_view.py` | Generates interactive layer views, SVGs, and a physical stackup diagram from a snapshot. |
| `audit_connections.py` | Compares pin and net inventories to find missing pins, wrong nets, and split or merged nets. |
| `run_spice.py` | Runs an ngspice deck and records the results, logs, and input hash. |

See the [tool reference](skills/lceda-hardware/references/tools.md) for commands and supported formats.

## Install

Clone this repository or download the standalone ZIP from [Releases](https://github.com/ziqidennisliu/lceda-hardware-skill/releases). With Python 3.10 or newer, run from the repository root:

```sh
python3 skills/lceda-hardware/scripts/install_skill.py --apply
```

For hosts using the personal Agents directory, pass `--destination ~/.agents/skills`. For the standalone ZIP, use `lceda-hardware/scripts/install_skill.py` instead. Install JLCEDA Pro desktop separately.

> Use $lceda-hardware to connect to JLCEDA Pro, inspect my design, and continue the authorized design stage. Ask about unresolved design decisions.

See the [setup guide](skills/lceda-hardware/references/setup.md) for connection and troubleshooting steps.

## Test

```sh
python3 skills/lceda-hardware/scripts/test_helpers.py
```

Live connection and PCB export were tested on macOS with JLCEDA Pro V4.1.78. Fresh dependency installation and live Windows/Linux connections remain unverified. See the [source and compatibility notes](skills/lceda-hardware/references/sources.md).
