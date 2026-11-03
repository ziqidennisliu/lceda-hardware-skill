# LCEDA Hardware Skill

An English-language agent skill and CLI toolkit for JLCEDA Pro desktop. The workflow covers MCP connection, requirements, component selection, pin-level schematics, SPICE, physical stackup, PCB placement and routing review, and BOM delivery.

## Install

Clone this repository or download the standalone ZIP from [Releases](https://github.com/ziqidennisliu/lceda-hardware-skill/releases). With Python 3.10 or newer, run from the repository root:

```sh
python3 skills/lceda-hardware/scripts/install_skill.py --apply
```

For hosts using the personal Agents directory, pass `--destination ~/.agents/skills`. For the standalone ZIP, use `lceda-hardware/scripts/install_skill.py` instead. Install JLCEDA Pro desktop separately.

> Use $lceda-hardware to connect to JLCEDA Pro, inspect my design, and continue the authorized design stage. Ask about unresolved design decisions.

The [skill](skills/lceda-hardware/SKILL.md) links to the [setup guide](skills/lceda-hardware/references/setup.md), [confirmation matrix](skills/lceda-hardware/references/confirmations.md), and [tool reference](skills/lceda-hardware/references/tools.md). Tools include guarded PCB export, interactive per-layer review, a physical stack diagram, a pin and net audit, and ngspice execution.

## Test

```sh
python3 skills/lceda-hardware/scripts/test_helpers.py
```

Live connection and PCB export were tested on macOS with JLCEDA Pro V4.1.78. Fresh dependency installation and live Windows/Linux connections remain unverified. See the [source and compatibility notes](skills/lceda-hardware/references/sources.md).
