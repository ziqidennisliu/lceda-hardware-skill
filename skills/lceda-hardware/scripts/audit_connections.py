#!/usr/bin/env python3
"""Compare complete, independently normalized physical-pin inventories. Stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path


def inventory(doc):
    rows = doc.get("pins")
    if not isinstance(rows, list) or not rows:
        raise ValueError("pins must be a non-empty list of ALL physical pins")
    found, errors = {}, []
    for row in rows:
        if not isinstance(row, dict):
            errors.append({"invalid_row": row})
            continue
        ref, pin = row.get("ref"), row.get("pin")
        if not isinstance(ref, str) or not ref or not isinstance(pin, str) or not pin:
            errors.append({"invalid_identity": row})
            continue
        key = (ref, pin)
        if key in found:
            errors.append({"duplicate_pin": list(key)})
        net, nc = row.get("net"), row.get("nc")
        if type(nc) is not bool:
            errors.append({"invalid_nc_flag": list(key)})
        if nc is True:
            if net not in (None, "") or not row.get("reason"):
                errors.append({"invalid_nc": list(key), "detail": "NC requires no net and a reason"})
            net = None
        elif not isinstance(net, str) or not net.strip():
            errors.append({"unassigned_pin": list(key)})
        found[key] = {"net": net, "nc": nc}
    return found, errors


def compare(expected, actual):
    e, ee = inventory(expected)
    a, ae = inventory(actual)
    shared = e.keys() & a.keys()
    changed = [{"ref": k[0], "pin": k[1], "expected": e[k], "actual": a[k]}
               for k in sorted(shared) if e[k] != a[k]]
    splits, merges = {}, {}
    for k in shared:
        if e[k]["net"] and a[k]["net"]:
            splits.setdefault(e[k]["net"], set()).add(a[k]["net"])
            merges.setdefault(a[k]["net"], set()).add(e[k]["net"])
    result = {
        "expected_errors": ee, "actual_errors": ae,
        "missing_pins": sorted(e.keys() - a.keys()),
        "unexpected_pins": sorted(a.keys() - e.keys()),
        "changed_pins": changed,
        "split_nets": {k: sorted(v) for k, v in splits.items() if len(v) > 1},
        "merged_nets": {k: sorted(v) for k, v in merges.items() if len(v) > 1},
    }
    result["passed"] = not any(result.values())
    result["counts"] = {"expected_pins": len(e), "actual_pins": len(a)}
    result["scope"] = "Pin identity/net/NC only; not geometry, component specifications, ERC or DRC"
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("expected", type=Path)
    p.add_argument("actual", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        result = compare(json.loads(args.expected.read_text()), json.loads(args.actual.read_text()))
        result["inputs"] = [{"path": str(x.resolve()), "sha256": hashlib.sha256(x.read_bytes()).hexdigest()}
                            for x in (args.expected, args.actual)]
    except (ValueError, OSError, TypeError) as exc:
        result = {"passed": False, "error": str(exc)}
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        if args.output.resolve() in (args.expected.resolve(), args.actual.resolve()):
            p.error("output must not overwrite an input")
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
