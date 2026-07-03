import contextlib
import io
import os
import tempfile
import unittest

from scripts.run_demo import load_named_value_profile, run_demo, select_candidate_patch


class RunDemoHelpersTest(unittest.TestCase):
    def test_candidate_selection_default_returns_recommended(self):
        proposal = {
            "recommended_patch": {"pattern": "two_column", "operations": []},
            "alternatives": [{"pattern": "hero_plus_support", "operations": []}],
        }
        self.assertEqual(select_candidate_patch(proposal, "")["pattern"], "two_column")

    def test_candidate_selection_can_pick_alternative(self):
        proposal = {
            "recommended_patch": {"pattern": "two_column", "operations": []},
            "alternatives": [{"pattern": "hero_plus_support", "operations": []}],
        }
        self.assertEqual(select_candidate_patch(proposal, "2")["pattern"], "hero_plus_support")

    def test_named_profile_loader_loads_valid_profile(self):
        profile = load_named_value_profile("minimal_fix")
        self.assertGreaterEqual(profile["only_fix_hard_errors"], 0.75)

    def test_visual_output_path_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repaired_path = os.path.join(tmpdir, "repaired.json")
            visual_path = os.path.join(tmpdir, "visual.html")
            with contextlib.redirect_stdout(io.StringIO()):
                run_demo(
                    "assets/demo_cases/case_01_ppt_content_before.json",
                    "assets/value_profiles/readability_first.json",
                    output_json=repaired_path,
                    visual_output=visual_path,
                )
            self.assertTrue(os.path.exists(repaired_path))
            self.assertTrue(os.path.exists(visual_path))


if __name__ == "__main__":
    unittest.main()
