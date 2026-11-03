#!/usr/bin/env python3
"""Export a guarded read-only PCB snapshot via the native CLI, without opening/saving."""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import bootstrap


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--eda-bin')
    p.add_argument('--session', required=True)
    p.add_argument('--project-uuid', required=True)
    p.add_argument('--pcb-uuid', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists() or a.output.suffix != '.json':
        p.error('output must be a NEW .json snapshot, never an EDA project/source file')
    eda = bootstrap.find_eda(a.eda_bin)
    # This wrapper calls only the fixed read-only payload, never accepts arbitrary JS.
    raw = bootstrap.run([eda, 'invoke', '--session', a.session, '--code-file', Path(__file__).with_name('export_pcb.js'),
        '--args', json.dumps({'projectUuid':a.project_uuid,'pcbUuid':a.pcb_uuid}), '--timeout', '60000'], timeout=70)
    result = bootstrap.unwrap(raw)
    data = gzip.decompress(base64.b64decode(result['gzip'], validate=True))
    doc = json.loads(data)
    if doc['pcb']['uuid'] != a.pcb_uuid or doc['project']['uuid'] != a.project_uuid:
        raise ValueError('Decoded target mismatch')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_bytes(data)
    print(json.dumps({'path':str(a.output.resolve()),'sha256':hashlib.sha256(data).hexdigest(),
        'components':len(doc['components']),'pcb_uuid':a.pcb_uuid,'read_only':True},indent=2))


if __name__ == '__main__':
    main()
