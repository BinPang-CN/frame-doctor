import unittest

from scripts.render_canvas_html import render_comparison, render_single_canvas


def sample_canvas(text="Body text"):
    return {
        "frame": {"id": "test", "width": 400, "height": 240},
        "nodes": [
            {"id": "title", "role": "title", "type": "text", "x": 24, "y": 24, "width": 220, "height": 44, "text": "Title"},
            {"id": "body", "role": "body", "type": "text", "x": 32, "y": 84, "width": 180, "height": 80, "text": text},
            {"id": "image", "role": "image", "type": "image", "x": 120, "y": 110, "width": 160, "height": 90},
        ],
    }


class RenderCanvasHtmlTest(unittest.TestCase):
    def test_render_single_canvas_contains_node_ids_and_roles(self):
        html = render_single_canvas(sample_canvas(), "Example")
        self.assertIn("title", html)
        self.assertIn("body", html)
        self.assertIn("role-title", html)
        self.assertIn("role-image", html)

    def test_render_comparison_contains_before_and_after_headings(self):
        html = render_comparison(sample_canvas(), sample_canvas())
        self.assertIn(">Before<", html)
        self.assertIn(">After<", html)
        self.assertIn("Metric Summary", html)

    def test_render_escapes_text_content(self):
        html = render_single_canvas(sample_canvas("<script>alert(1)</script>"), "Escaping")
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)

    def test_render_includes_conflict_summary(self):
        html = render_single_canvas(sample_canvas(), "Conflicts")
        self.assertIn("Conflict Summary", html)
        self.assertIn("Overlaps", html)
        self.assertIn("Critical", html)


if __name__ == "__main__":
    unittest.main()
