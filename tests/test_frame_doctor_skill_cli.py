import json
import os
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(REPO_ROOT, "scripts", "frame_doctor_skill.py")
BROKEN_DEMO = os.path.join(REPO_ROOT, "assets", "demo_cases", "case_01_ppt_content_before.json")
READABILITY_PROFILE = os.path.join(REPO_ROOT, "assets", "value_profiles", "readability_first.json")


def run_cli(*args):
    return subprocess.run(
        [sys.executable, CLI, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class FrameDoctorSkillCliTest(unittest.TestCase):
    def test_generation_brief_includes_forbidden_hard_errors(self):
        result = run_cli("generation-brief", "--target", "ppt", "--profile", "readability_first")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        forbidden = payload["layout_generation_constraints"]["forbidden"]
        self.assertIn("overlap", forbidden)
        self.assertIn("out_of_bounds", forbidden)
        self.assertIn("text_overflow", forbidden)
        self.assertTrue(payload["layout_generation_constraints"]["audit_required"])

    def test_guard_returns_critical_count_for_broken_demo(self):
        result = run_cli("guard", BROKEN_DEMO, "--profile", "readability_first")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreater(payload["critical_count"], 0)
        self.assertFalse(payload["ok"])

    def test_guard_fail_on_critical_exits_nonzero(self):
        result = run_cli("guard", BROKEN_DEMO, "--profile", "readability_first", "--fail-on-critical")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertGreater(payload["critical_count"], 0)

    def test_repair_writes_repaired_json_and_visual_html(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repaired = os.path.join(tmpdir, "repaired.json")
            visual = os.path.join(tmpdir, "comparison.html")
            result = run_cli(
                "repair",
                BROKEN_DEMO,
                "--profile",
                "readability_first",
                "--output",
                repaired,
                "--visual-output",
                visual,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["output"], repaired)
            self.assertTrue(os.path.exists(repaired))
            self.assertTrue(os.path.exists(visual))
            self.assertEqual(payload["critical_after"], 0)

    def test_profile_loads_by_name_and_path(self):
        by_name = run_cli("propose", BROKEN_DEMO, "--profile", "readability_first")
        by_path = run_cli("propose", BROKEN_DEMO, "--profile", READABILITY_PROFILE)
        self.assertEqual(by_name.returncode, 0, by_name.stderr)
        self.assertEqual(by_path.returncode, 0, by_path.stderr)
        self.assertEqual(
            json.loads(by_name.stdout)["recommended_patch"]["pattern"],
            json.loads(by_path.stdout)["recommended_patch"]["pattern"],
        )


if __name__ == "__main__":
    unittest.main()
