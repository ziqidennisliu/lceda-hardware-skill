# Reference case: a shared impedance-sensing board

This is a generalized retrospective of an impedance-watch project developed in October 2026, summarized on November 4, 2026. Private libraries, native designs, account data, session IDs, and machine-specific paths are not distributed. New projects start from their own requirements and live state.

## Design evolution

1. The EITWatch reference informed a DDS, programmable gain, Howland current source, sensing amplifier, and ADC architecture. The MCU was external; PPG was represented only by a mechanical window.
2. Initial H/V sensing paths were separate. H included contact plus tissue paths; V represented a loaded four-terminal transfer response rather than isolated pure tissue impedance.
3. The initial 50 kHz target expanded to 20–100 kHz with H loads of 1–50 kilohms. Later 5/10 kHz checks reinforced the distinction between programmable frequency and a validated range/gain/accuracy domain.
4. V-channel checks exposed finite input impedance, imbalance, and common-mode effects. Shared switched sensing reduced some loading without removing body-path or residual capacitive coupling.
5. An intermediate high-voltage mux required a 12 V supply and additional ADC drive circuitry. Simplification moved to low-voltage selection, shared post-selection coupling, and a single ADC path, removing unnecessary debug/peripheral structures. Every revision rechecked voltage ranges, bias returns, and ADC limits.
6. Package reduction followed the reference where ratings allowed, while retaining necessary precision/storage parts and testing effective MLCC capacitance. Replacing a four-pin header with individual electrode pads required updated procurement properties and connectivity checks.
7. Work progressed from module separation to local loops, two-sided placement in an AFE extension, six layers, internal copper, regular routing, native fill, and DRC. Manufacturing/mechanical and physical performance acceptance remained separate.

## Lessons and corresponding checks

| Observation | Reusable response |
|---|---|
| Foreign-net stubs touched while export still kept nets separate | Audit semantics and geometry; describe ambiguity rather than invent a confirmed short |
| H-only verification was insufficient | Cover V, all control states, contact perturbations, input imbalance, and common mode |
| Larger bias resistors allowed off-state drift | Jointly assess loading, leakage, common-node bias, switching peaks, and settling |
| Reference topology was assumed to imply correct output range | Revalidate present supplies, INA common mode, and ADC acquisition |
| Smaller capacitors changed effective capacitance | Review terminal bias, matching, storage, and frequency behavior |
| Sync/generators could restore old selections | Update the authoritative manifest/generator and freeze historical reports |
| Bottom labels remained reversed after flipping | Check parent/label transforms on one instance before applying broadly |
| More copper layers still left a two-layer material stack | Validate logical and physical layers independently |
| POUR boundaries did not establish filled copper | Rebuild and inspect actual POURED, including separate islands |
| Autorouter continued after timeout | Inspect job/object progress before retrying |
| Copper paths passed while drill sizes failed | Check drills, annuli, hole spacing, and per-layer keepouts |
| Old reports contradicted current state | Maintain one version/hash-bound current entry point |

The historical initial-routing report recorded 83 physical PCB components, 255 pads, 57 nets, 3 NCs, 710 line segments, 119 through vias, and 8 rebuilt pours with zero native strict DRC violations. There were 79 soldered components, four copper electrodes, and a separately purchased MCU.

These are historical acceptance counts, not requirements for another board. Behavioral comparison also found some contact-perturbation metrics worse after simplification, and an expanded 100-kilohm load exceeded range. Fewer parts and complete connectivity do not prove better isolation or accuracy.

This repository contains workflow lessons, not EITWatch source files. Obtain any desired reference hardware from its original repository under the applicable license and attribution terms.
