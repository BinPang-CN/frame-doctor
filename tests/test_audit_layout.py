import unittest

from scripts.apply_patch_to_json import apply_patch_to_canvas
from scripts.audit_layout import audit_layout
from scripts.propose_layout_patch import propose_layout_patch


class AuditLayoutTest(unittest.TestCase):
    def test_audit_layout_returns_scores_and_remaining_conflicts(self):
        before = {
            "frame": {"id": "test", "width": 500, "height": 360},
            "nodes": [
                {"id": "a", "role": "card", "x": 40, "y": 80, "width": 160, "height": 100},
                {"id": "b", "role": "card", "x": 90, "y": 100, "width": 160, "height": 100},
            ],
        }
        proposal = propose_layout_patch(before, {"only_fix_hard_errors": 0.9})
        after = apply_patch_to_canvas(before, proposal["recommended_patch"])
        report = audit_layout(before, after)
        self.assertIn("before_score", report)
        self.assertIn("after_score", report)
        self.assertIn("score_delta", report)
        self.assertIn("remaining_conflicts", report)

    def test_overlap_area_reduction_is_positive_after_repair(self):
        before = {
            "frame": {"id": "test", "width": 500, "height": 360},
            "nodes": [
                {"id": "a", "role": "card", "x": 40, "y": 80, "width": 160, "height": 100},
                {"id": "b", "role": "card", "x": 90, "y": 100, "width": 160, "height": 100},
            ],
        }
        proposal = propose_layout_patch(before, {"only_fix_hard_errors": 0.9})
        after = apply_patch_to_canvas(before, proposal["recommended_patch"])
        report = audit_layout(before, after)
        self.assertGreater(report["metric_deltas"]["overlap_area_reduction"], 0)


if __name__ == "__main__":
    unittest.main()
