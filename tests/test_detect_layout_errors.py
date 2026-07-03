import unittest

from scripts.detect_layout_errors import detect_layout_errors


class DetectLayoutErrorsTest(unittest.TestCase):
    def test_overlap_can_be_detected(self):
        canvas = {
            "frame": {"id": "test", "width": 400, "height": 300},
            "nodes": [
                {"id": "a", "role": "card", "x": 10, "y": 10, "width": 100, "height": 100},
                {"id": "b", "role": "card", "x": 60, "y": 60, "width": 100, "height": 100},
            ],
        }
        report = detect_layout_errors(canvas)
        self.assertEqual(report["summary"].get("overlap_count"), 1)

    def test_out_of_bounds_can_be_detected(self):
        canvas = {
            "frame": {"id": "test", "width": 400, "height": 300},
            "nodes": [
                {"id": "a", "role": "image", "x": 350, "y": 20, "width": 100, "height": 80}
            ],
        }
        report = detect_layout_errors(canvas)
        self.assertEqual(report["summary"].get("out_of_bounds_count"), 1)

    def test_no_conflicts_has_zero_error_count(self):
        canvas = {
            "frame": {"id": "test", "width": 400, "height": 300},
            "nodes": [
                {"id": "a", "role": "title", "x": 20, "y": 20, "width": 160, "height": 40},
                {"id": "b", "role": "image", "x": 220, "y": 80, "width": 120, "height": 120},
            ],
        }
        report = detect_layout_errors(canvas)
        self.assertEqual(report["summary"]["error_count"], 0)

    def test_declared_safe_margin_breach_can_be_detected(self):
        canvas = {
            "frame": {"id": "test", "width": 400, "height": 300, "safe_margin": 32},
            "nodes": [
                {"id": "a", "role": "title", "x": 12, "y": 40, "width": 120, "height": 40}
            ],
        }
        report = detect_layout_errors(canvas)
        self.assertEqual(report["summary"].get("margin_breach_count"), 1)

    def test_alignment_drift_can_be_detected_for_repeated_cards(self):
        canvas = {
            "frame": {"id": "test", "width": 600, "height": 400},
            "nodes": [
                {"id": "card_1", "role": "card", "x": 40, "y": 80, "width": 120, "height": 80},
                {"id": "card_2", "role": "card", "x": 184, "y": 92, "width": 120, "height": 80},
                {"id": "card_3", "role": "card", "x": 328, "y": 80, "width": 120, "height": 80},
            ],
        }
        report = detect_layout_errors(canvas)
        self.assertGreaterEqual(report["summary"].get("alignment_drift_count", 0), 1)

    def test_gutter_anomaly_can_be_detected_for_repeated_cards(self):
        canvas = {
            "frame": {"id": "test", "width": 800, "height": 400},
            "nodes": [
                {"id": "card_1", "role": "card", "x": 40, "y": 80, "width": 100, "height": 80},
                {"id": "card_2", "role": "card", "x": 160, "y": 80, "width": 100, "height": 80},
                {"id": "card_3", "role": "card", "x": 360, "y": 80, "width": 100, "height": 80},
            ],
        }
        report = detect_layout_errors(canvas)
        self.assertGreaterEqual(report["summary"].get("gutter_anomaly_count", 0), 1)

    def test_baseline_mismatch_can_be_detected_when_metadata_exists(self):
        canvas = {
            "frame": {"id": "test", "width": 400, "height": 300},
            "layout_metadata": {"baseline_grid": 8},
            "nodes": [
                {"id": "title", "role": "title", "type": "text", "x": 40, "y": 21, "width": 200, "height": 40}
            ],
        }
        report = detect_layout_errors(canvas)
        self.assertEqual(report["summary"].get("baseline_mismatch_count"), 1)

    def test_hierarchy_ambiguity_can_be_detected(self):
        canvas = {
            "frame": {"id": "test", "width": 600, "height": 400},
            "nodes": [
                {"id": "title", "role": "title", "type": "text", "font_size": 18, "x": 40, "y": 40, "width": 200, "height": 30},
                {"id": "body", "role": "body", "type": "text", "font_size": 24, "x": 40, "y": 100, "width": 300, "height": 80},
            ],
        }
        report = detect_layout_errors(canvas)
        self.assertGreaterEqual(report["summary"].get("hierarchy_ambiguity_count", 0), 1)


if __name__ == "__main__":
    unittest.main()
