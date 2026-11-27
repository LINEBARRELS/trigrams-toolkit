"""Unit tests for the axiomatic-audit deterministic matrix solver and Skill metadata."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOLVER_PATH = ROOT / "skills/axiomatic-audit/scripts/matrix_solver.py"

spec = importlib.util.spec_from_file_location("axiomatic_matrix_solver", SOLVER_PATH)
assert spec is not None and spec.loader is not None
solver = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = solver
spec.loader.exec_module(solver)


class AxiomaticMatrixSolverTests(unittest.TestCase):
    def test_paired_uncoupled_diagonal_matrix(self) -> None:
        payload = {
            "scope": "module",
            "frs": [
                {"id": "FR1", "name": "Parsing"},
                {"id": "FR2", "name": "Rendering"},
            ],
            "dps": [
                {"id": "DP1", "name": "parser"},
                {"id": "DP2", "name": "renderer"},
            ],
            "edges": [],
        }
        result = solver.analyze_design_matrix(payload)
        self.assertTrue(result["ok"])
        self.assertEqual(result["mode"], "paired")
        self.assertEqual(result["summary"]["full_classification"], "uncoupled")
        self.assertEqual(result["full_view"]["matrix"], [["●", "·"], ["·", "●"]])
        self.assertEqual(result["full_view"]["upper_triangular_violations"], [])

    def test_paired_scrambled_dag_reorders_to_strict_lower_triangular(self) -> None:
        # Presentation (FR1) -> Orchestration (FR2) -> Domain (FR3), given top-down in reverse order.
        payload = {
            "scope": "layer",
            "frs": [
                {"id": "FR1", "name": "Presentation"},
                {"id": "FR2", "name": "Orchestration"},
                {"id": "FR3", "name": "Domain"},
            ],
            "dps": [
                {"id": "DP1", "name": "ui/"},
                {"id": "DP2", "name": "app/"},
                {"id": "DP3", "name": "domain/"},
            ],
            "edges": [
                {"fr": "FR1", "dp": "DP2", "kind": "D", "evidence": "ui/view.py:10"},
                {"fr": "FR2", "dp": "DP3", "kind": "D", "evidence": "app/service.py:18"},
                {"fr": "FR1", "dp": "DP3", "kind": "D", "evidence": "ui/view.py:12"},
            ],
        }
        result = solver.analyze_design_matrix(payload)
        self.assertEqual(result["summary"]["full_classification"], "decoupled")
        ordered_fr_ids = [item["id"] for item in result["full_view"]["ordered_frs"]]
        ordered_dp_ids = [item["id"] for item in result["full_view"]["ordered_dps"]]
        self.assertEqual(ordered_fr_ids, ["FR3", "FR2", "FR1"])
        self.assertEqual(ordered_dp_ids, ["DP3", "DP2", "DP1"])
        self.assertEqual(
            result["full_view"]["matrix"],
            [
                ["●", "·", "·"],
                ["D", "●", "·"],
                ["D", "D", "●"],
            ],
        )
        self.assertEqual(result["full_view"]["upper_triangular_violations"], [])

    def test_paired_hidden_change_coupling_escalates_dag_to_coupled(self) -> None:
        payload = {
            "scope": "module",
            "frs": [
                {"id": "FR1", "name": "Domain Rules"},
                {"id": "FR2", "name": "CLI Runner"},
                {"id": "FR3", "name": "Bootstrap", "ard_ref": "docs/ARD.md#L5"},
            ],
            "dps": [
                {"id": "DP1", "name": "src/domain"},
                {"id": "DP2", "name": "src/cli"},
                {"id": "DP3", "name": "src/bootstrap", "role": "arch"},
            ],
            "edges": [
                {"fr": "FR2", "dp": "DP1", "kind": "D", "evidence": "src/cli/main.py:8"},
                {"fr": "FR3", "dp": "DP2", "kind": "D", "evidence": "src/bootstrap/app.py:4"},
                # Hidden change coupling: changing Domain rule forces parallel enum edit in CLI.
                {"fr": "FR1", "dp": "DP2", "kind": "C", "evidence": "src/domain/status.py:5 <-> src/cli/main.py:44"},
            ],
        }
        result = solver.analyze_design_matrix(payload)
        self.assertEqual(result["summary"]["explicit_only_classification"], "decoupled")
        self.assertEqual(result["summary"]["full_classification"], "coupled")
        self.assertTrue(result["summary"]["hidden_coupling_escalation"])
        self.assertEqual(result["summary"]["scc_count"], 1)
        scc_members = {m["fr"] for m in result["full_view"]["cyclic_sccs"][0]["members"]}
        self.assertEqual(scc_members, {"FR1", "FR2"})
        self.assertEqual(len(result["full_view"]["upper_triangular_violations"]), 1)
        # Bootstrap (FR3) sits outside the cycle at the bottom-right.
        self.assertEqual(result["full_view"]["ordered_frs"][-1]["id"], "FR3")

    def test_bipartite_redundant_shared_upstream_is_decoupled(self) -> None:
        # Two independent turrets (DP2, DP3) on one shared ship hull (DP1) => decoupled, redundant.
        payload = {
            "scope": "feature",
            "mode": "bipartite",
            "frs": [
                {"id": "FR1", "name": "Aim Bow Turret"},
                {"id": "FR2", "name": "Aim Stern Turret"},
            ],
            "dps": [
                {"id": "DP1", "name": "Ship Hull"},
                {"id": "DP2", "name": "Bow Turret"},
                {"id": "DP3", "name": "Stern Turret"},
            ],
            "edges": [
                {"fr": "FR1", "dp": "DP1", "kind": "D", "evidence": "ship.py:10"},
                {"fr": "FR1", "dp": "DP2", "kind": "D", "evidence": "ship.py:20"},
                {"fr": "FR2", "dp": "DP1", "kind": "D", "evidence": "ship.py:12"},
                {"fr": "FR2", "dp": "DP3", "kind": "D", "evidence": "ship.py:30"},
            ],
        }
        result = solver.analyze_design_matrix(payload)
        self.assertEqual(result["summary"]["full_classification"], "decoupled")
        self.assertEqual(result["full_view"]["redundant_dp_count"], 1)
        self.assertEqual(result["full_view"]["upper_triangular_violations"], [])
        self.assertEqual(result["full_view"]["ordered_dps"][0]["id"], "DP1")

    def test_bipartite_theorem1_deficient_and_hall_bottleneck(self) -> None:
        # Pirate ship: 2 FRs (Heading, Aim) controlled by 1 DP (Rudder) -> Theorem 1 coupled.
        payload = {
            "scope": "feature",
            "mode": "bipartite",
            "frs": [
                {"id": "FR1", "name": "Control Heading"},
                {"id": "FR2", "name": "Aim Broadside"},
            ],
            "dps": [
                {"id": "DP1", "name": "Rudder"},
            ],
            "edges": [
                {"fr": "FR1", "dp": "DP1", "kind": "D", "evidence": "hull.py:5"},
                {"fr": "FR2", "dp": "DP1", "kind": "D", "evidence": "hull.py:9"},
            ],
        }
        result = solver.analyze_design_matrix(payload)
        self.assertEqual(result["summary"]["full_classification"], "coupled")
        self.assertTrue(result["full_view"]["deficient_design"])
        self.assertIsNotNone(result["full_view"]["hall_bottleneck"])
        self.assertEqual(len(result["full_view"]["hall_bottleneck"]["frs"]), 2)
        self.assertEqual(len(result["full_view"]["hall_bottleneck"]["dps"]), 1)

    def test_bipartite_coupled_core_isolates_peeled_tail(self) -> None:
        # FR1 & FR2 are mutually coupled on DP1 & DP2; FR3 depends on DP2 + its own DP3.
        payload = {
            "scope": "feature",
            "mode": "bipartite",
            "frs": [
                {"id": "FR1", "name": "State A"},
                {"id": "FR2", "name": "State B"},
                {"id": "FR3", "name": "Export"},
            ],
            "dps": [
                {"id": "DP1", "name": "Store X"},
                {"id": "DP2", "name": "Store Y"},
                {"id": "DP3", "name": "Exporter"},
            ],
            "edges": [
                {"fr": "FR1", "dp": "DP1", "kind": "D", "evidence": "a.py:1"},
                {"fr": "FR1", "dp": "DP2", "kind": "C", "evidence": "a.py:2"},
                {"fr": "FR2", "dp": "DP1", "kind": "C", "evidence": "b.py:1"},
                {"fr": "FR2", "dp": "DP2", "kind": "D", "evidence": "b.py:2"},
                {"fr": "FR3", "dp": "DP2", "kind": "D", "evidence": "c.py:1"},
                {"fr": "FR3", "dp": "DP3", "kind": "D", "evidence": "c.py:2"},
            ],
        }
        result = solver.analyze_design_matrix(payload)
        self.assertEqual(result["summary"]["full_classification"], "coupled")
        self.assertEqual(result["summary"]["scc_count"], 1)
        self.assertEqual(result["full_view"]["ordered_frs"][-1]["id"], "FR3")
        self.assertEqual(result["full_view"]["ordered_dps"][-1]["id"], "DP3")

    def test_drift_tracks_phantom_frs_and_wild_dps(self) -> None:
        payload = {
            "scope": "module",
            "frs": [
                {"id": "FR1", "name": "Core"},
                {"id": "FR2", "name": "Planned Only", "ard_ref": "docs/ARD.md#L40", "status": "phantom"},
            ],
            "dps": [
                {"id": "DP1", "name": "src/core"},
                {"id": "DP2", "name": "src/secret_helper", "paths": ["src/secret_helper"], "status": "wild"},
            ],
            "edges": [
                {"fr": "FR1", "dp": "DP2", "kind": "D", "evidence": "src/core/x.py:3"},
            ],
        }
        result = solver.analyze_design_matrix(payload)
        self.assertEqual(result["summary"]["phantom_fr_count"], 1)
        self.assertEqual(result["summary"]["wild_dp_count"], 1)
        self.assertTrue(result["drift"]["wild_dps"][0]["coupled_to_active_fr"])
        self.assertEqual(len(result["full_view"]["wild_dp_couplings"]), 1)

    def test_validation_rejects_missing_evidence_and_unknown_ids(self) -> None:
        base = {
            "scope": "module",
            "frs": [{"id": "FR1", "name": "A"}],
            "dps": [{"id": "DP1", "name": "a"}],
            "edges": [{"fr": "FR1", "dp": "DP1", "kind": "D", "evidence": ""}],
        }
        with self.assertRaises(ValueError):
            solver.analyze_design_matrix(base)
        bad_ref = {**base, "edges": [{"fr": "FR9", "dp": "DP1", "kind": "D", "evidence": "a.py:1"}]}
        with self.assertRaises(ValueError):
            solver.analyze_design_matrix(bad_ref)

    def test_cli_writes_json_and_markdown_outputs(self) -> None:
        payload = {
            "scope": "module",
            "title": "CLI Smoke Test",
            "frs": [{"id": "FR1", "name": "Base"}, {"id": "FR2", "name": "App"}],
            "dps": [{"id": "DP1", "name": "base/"}, {"id": "DP2", "name": "app/"}],
            "edges": [{"fr": "FR2", "dp": "DP1", "kind": "D", "evidence": "app/main.py:1"}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            in_path = tmp_path / "input.json"
            json_out = tmp_path / "out/result.json"
            md_out = tmp_path / "out/matrix.md"
            in_path.write_text(json.dumps(payload), encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(SOLVER_PATH), str(in_path), "--json-out", str(json_out), "--md-out", str(md_out)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            parsed_stdout = json.loads(completed.stdout)
            self.assertEqual(parsed_stdout["summary"]["full_classification"], "decoupled")
            self.assertTrue(json_out.is_file())
            self.assertTrue(md_out.is_file())
            md_text = md_out.read_text(encoding="utf-8")
            self.assertIn("## Reordered Design Matrix (D+C)", md_text)
            self.assertIn("`FR1` Base", md_text)

    def test_skill_frontmatter_and_cohesion_contract(self) -> None:
        skill_md = ROOT / "skills/axiomatic-audit/SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        self.assertIn("name: axiomatic-audit", text)
        self.assertIn("disable-model-invocation: true", text)
        self.assertIn("PRODUCT.md", text)
        self.assertIn(".tmp/axiomatic-audit/", text)
        self.assertIn("answer-me-with-html", text)
        for internal_ref in ("project-state", "plan-toolkit", "handbook", "core:principle:", "core:workbook:"):
            self.assertNotIn(internal_ref, text)


if __name__ == "__main__":
    unittest.main()
