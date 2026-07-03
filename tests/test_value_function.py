import unittest

from scripts.propose_layout_patch import propose_layout_patch
from scripts.value_function import normalize_profile, rank_candidates


class ValueFunctionTest(unittest.TestCase):
    def test_readability_prefers_two_column_over_hero(self):
        canvas = {
            "frame": {"id": "slide", "width": 1200, "height": 800},
            "nodes": [
                {"id": "title", "role": "title", "type": "text", "x": 80, "y": 60, "width": 600, "height": 60},
                {"id": "body", "role": "body", "type": "text", "x": 80, "y": 160, "width": 460, "height": 300},
                {"id": "image", "role": "image", "x": 600, "y": 160, "width": 420, "height": 300},
            ],
        }
        candidates = [
            {"pattern": "hero_plus_support", "confidence": 0.84, "reason": "hero"},
            {"pattern": "two_column", "confidence": 0.8, "reason": "columns"},
        ]
        ranked = rank_candidates(candidates, {"readability": 0.95, "visual_impact": 0.2}, canvas)
        self.assertEqual(ranked[0]["pattern"], "two_column")

    def test_density_prefers_grid_or_dashboard(self):
        canvas = {
            "frame": {"id": "dash", "width": 1200, "height": 800},
            "nodes": [
                {"id": f"card_{index}", "role": "card", "x": 40 + index * 120, "y": 80, "width": 100, "height": 80}
                for index in range(4)
            ],
        }
        proposal = propose_layout_patch(canvas, {"density": 0.95, "grid_strictness": 0.85})
        self.assertIn(proposal["structure_candidates"][0]["pattern"], ("dashboard", "card_grid"))

    def test_minimal_fix_uses_minimal_patch_builder(self):
        canvas = {
            "frame": {"id": "slide", "width": 400, "height": 300},
            "nodes": [
                {"id": "a", "role": "card", "x": 20, "y": 20, "width": 160, "height": 120},
                {"id": "b", "role": "card", "x": 80, "y": 60, "width": 160, "height": 120},
            ],
        }
        profile = normalize_profile({"only_fix_hard_errors": 0.9, "content_preservation": 0.95})
        proposal = propose_layout_patch(canvas, profile)
        self.assertEqual(proposal["recommended_patch"]["pattern"], "minimal_fix")
        self.assertLessEqual(len(proposal["recommended_patch"]["operations"]), 2)

    def test_patch_output_contains_value_metadata_and_no_forbidden_ops(self):
        canvas = {
            "frame": {"id": "slide", "width": 400, "height": 300},
            "nodes": [
                {"id": "title", "role": "title", "type": "text", "x": 20, "y": 20, "width": 160, "height": 40},
                {"id": "body", "role": "body", "type": "text", "x": 20, "y": 80, "width": 160, "height": 100},
                {"id": "image", "role": "image", "x": 220, "y": 80, "width": 120, "height": 120},
            ],
        }
        proposal = propose_layout_patch(canvas, {"readability": 0.9})
        patch = proposal["recommended_patch"]
        self.assertIn("value_profile_used", patch)
        self.assertIn("value_tradeoffs", patch)
        forbidden = {"delete_content", "rewrite_text", "replace_image", "change_brand_style", "flatten_editable_layers"}
        self.assertFalse(any(operation.get("op") in forbidden for operation in patch["operations"]))


if __name__ == "__main__":
    unittest.main()
