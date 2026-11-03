#!/usr/bin/env python3
"""Run a reviewed SPICE deck; preserve logs and hashes, without claiming circuit acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('deck', type=Path)
    p.add_argument('--ngspice', required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--timeout', type=int, default=120)
    a = p.parse_args()
    deck = a.deck.resolve()
    if a.output_dir.exists():
        p.error('Use a new output directory; existing simulation results are preserved')
    a.output_dir.mkdir(parents=True)
    out = a.output_dir.resolve()
    log = out/'ngspice.log'
    # Run in deck directory so relative .include paths retain their intended meaning.
    result = {'deck':str(deck),'deck_sha256':hashlib.sha256(deck.read_bytes()).hexdigest(),
              'working_directory':str(deck.parent),'circuit_accepted':False,
              'note':'Review thresholds/waveforms; .include models must be registered separately. Deck .control output paths remain as authored.'}
    try:
        command = [a.ngspice, '-b', '-o', str(log), str(deck)]
        run = subprocess.run(command, cwd=deck.parent, capture_output=True, text=True, timeout=a.timeout)
        (out/'process.log').write_text(run.stdout + '\n' + run.stderr)
        text = log.read_text(errors='replace') if log.exists() else ''
        errors = re.findall(r'^.*(?:fatal error|Error on line|Error:|aborted|no simulations run).*$' ,text,re.M|re.I)
        result.update(exit_code=run.returncode, errors=errors,
                      process_completed=(run.returncode == 0 and bool(text) and not errors))
    except (OSError, subprocess.TimeoutExpired) as exc:
        result.update(process_completed=False,error=f'{type(exc).__name__}: {exc}')
    (out/'run-result.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    return 0 if result['process_completed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
