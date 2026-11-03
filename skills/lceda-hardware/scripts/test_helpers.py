#!/usr/bin/env python3
"""Offline behavioral checks. No live EDA mutations or network access."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import audit_connections as audit
import bootstrap
import install_skill
import pcb_view


BASE = {"pins": [
    {"ref": "R1", "pin": "1", "net": "VCC", "nc": False},
    {"ref": "R1", "pin": "2", "net": "X", "nc": False},
    {"ref": "R2", "pin": "1", "net": "X", "nc": False},
    {"ref": "R2", "pin": "2", "net": "GND", "nc": False},
    {"ref": "U1", "pin": "7", "net": None, "nc": True, "reason": "Datasheet NC"}
]}


class PinAudit(unittest.TestCase):
    def test_equal_permuted(self):
        actual = copy.deepcopy(BASE)
        actual["pins"].reverse()
        self.assertTrue(audit.compare(BASE, actual)["passed"])

    def test_missing(self):
        actual = copy.deepcopy(BASE)
        actual["pins"].pop()
        self.assertFalse(audit.compare(BASE, actual)["passed"])

    def test_unexpected(self):
        actual = copy.deepcopy(BASE)
        actual["pins"].append({"ref": "R9", "pin": "1", "net": "GND", "nc": False})
        self.assertTrue(audit.compare(BASE, actual)["unexpected_pins"])

    def test_nc_connected(self):
        actual = copy.deepcopy(BASE)
        actual["pins"][-1].update(net="GND", nc=False)
        self.assertTrue(audit.compare(BASE, actual)["changed_pins"])

    def test_duplicate(self):
        actual = copy.deepcopy(BASE)
        actual["pins"].append(actual["pins"][0])
        self.assertTrue(audit.compare(BASE, actual)["actual_errors"])

    def test_merge(self):
        actual = copy.deepcopy(BASE)
        actual["pins"][0]["net"] = "X"
        self.assertEqual(audit.compare(BASE, actual)["merged_nets"], {"X": ["VCC", "X"]})

    def test_split(self):
        actual = copy.deepcopy(BASE)
        actual["pins"][1]["net"] = "X2"
        self.assertEqual(audit.compare(BASE, actual)["split_nets"], {"X": ["X", "X2"]})

    def test_empty_not_pass(self):
        with self.assertRaises(ValueError):
            audit.compare({"pins": []}, {"pins": []})

    def test_nc_needs_reason(self):
        actual = copy.deepcopy(BASE)
        actual["pins"][-1].pop("reason")
        self.assertFalse(audit.compare(BASE, actual)["passed"])


class Installation(unittest.TestCase):
    def test_copy_idempotence_and_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, dest = root/"source/lceda-hardware", root/"skills"
            source.mkdir(parents=True)
            (source/"SKILL.md").write_text("test")
            install_skill.install(source, dest, False)
            self.assertFalse(dest.exists())
            install_skill.install(source, dest, True)
            install_skill.install(source, dest, True)
            (dest/"lceda-hardware/SKILL.md").write_text("user change")
            with self.assertRaises(RuntimeError):
                install_skill.install(source, dest, True)
            self.assertEqual((dest/"lceda-hardware/SKILL.md").read_text(), "user change")

    def test_registry_preserve(self):
        eda = Path('/example/eda')
        self.assertEqual(bootstrap.registration_status([], eda), 'missing')
        rows = [{"name": "jlceda", "transport": {"command": str(eda), "args": ["--mcp", "stdio"]}}]
        self.assertEqual(bootstrap.registration_status(rows, eda), 'reused')
        rows[0]["transport"]["command"] = '/another/server'
        with self.assertRaises(bootstrap.SetupError):
            bootstrap.registration_status(rows, eda)

    def test_business_error(self):
        with self.assertRaises(bootstrap.SetupError):
            bootstrap.unwrap('{"ok":false,"error":{"code":"REQUEST_TIMEOUT"}}')

    def test_envelopes(self):
        for key in ('data', 'value'):
            self.assertEqual(bootstrap.unwrap(json.dumps({'ok': True, key: {'connected': True}})), {'connected': True})

    def test_simulation_dry_no_writes(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(bootstrap, 'find_conda', return_value=None), patch.object(bootstrap, 'fetch', side_effect=AssertionError('network forbidden')):
            root = Path(tmp)
            report = bootstrap.simulation(root, False, True)
            self.assertTrue(report['install_conda_if_missing'])
            self.assertEqual(list(root.iterdir()), [])

    def test_space_guard_before_network(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(bootstrap,'find_conda',return_value=None), patch.object(bootstrap.shutil,'disk_usage') as usage, patch.object(bootstrap,'fetch',side_effect=AssertionError('network forbidden')):
            usage.return_value.free=100
            with self.assertRaisesRegex(bootstrap.SetupError,'Insufficient disk'):
                bootstrap.simulation(Path(tmp),True,True)


class Geometry(unittest.TestCase):
    def test_arc_endpoint_and_scale(self):
        pts=pcb_view.points([0,0,'ARC',90,10,10],.0254)
        self.assertEqual(pts[0],(0,0))
        self.assertEqual(pts[-1],(.254,.254))
        self.assertGreater(len(pts),2)

    def test_unknown_path_rejected(self):
        with self.assertRaises(ValueError):
            pcb_view.points([0,0,'SPLINE',1,2],1)

    def test_full_circle_ambiguous(self):
        with self.assertRaises(ValueError):
            pcb_view.points([0,0,'ARC',360,0,0],1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
