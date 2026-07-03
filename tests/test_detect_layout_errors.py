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


if __name__ == "__main__":
    unittest.main()
