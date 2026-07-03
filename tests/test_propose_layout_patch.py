import unittest

from scripts.propose_layout_patch import candidate_patterns, propose_layout_patch


class ProposeLayoutPatchTest(unittest.TestCase):
    def test_mobile_product_roles_suggest_ecommerce_flow(self):
        canvas = {
            "frame": {"id": "phone", "width": 375, "height": 812},
            "nodes": [
                {"id": "title", "role": "title", "x": 24, "y": 64, "width": 220, "height": 40},
                {"id": "product_1", "role": "product_card", "x": 24, "y": 128, "width": 150, "height": 220},
                {"id": "product_2", "role": "product_card", "x": 198, "y": 128, "width": 150, "height": 220},
                {"id": "checkout", "role": "checkout_summary", "x": 24, "y": 640, "width": 327, "height": 88},
            ],
        }
        patterns = candidate_patterns(canvas)
        self.assertEqual(patterns[0]["pattern"], "mobile_ecommerce_flow")

    def test_mobile_specific_pattern_uses_mobile_patch_builder(self):
        canvas = {
            "frame": {"id": "phone", "width": 375, "height": 812},
            "nodes": [
                {"id": "headline", "role": "title", "x": 24, "y": 80, "width": 260, "height": 44},
                {"id": "email", "role": "form_field", "x": 24, "y": 200, "width": 327, "height": 44},
                {"id": "password", "role": "form_field", "x": 24, "y": 260, "width": 327, "height": 44},
            ],
        }
        proposal = propose_layout_patch(canvas)
        self.assertEqual(proposal["recommended_patch"]["pattern"], "mobile_auth_form")
        self.assertEqual(proposal["structure_candidates"][0]["pattern"], "mobile_auth_form")


if __name__ == "__main__":
    unittest.main()
