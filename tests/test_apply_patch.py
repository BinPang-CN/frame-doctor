import unittest

from scripts.apply_patch_to_json import apply_patch_to_canvas


class ApplyPatchTest(unittest.TestCase):
    def test_move_resize_changes_geometry(self):
        canvas = {
            "frame": {"id": "test", "width": 400, "height": 300},
            "nodes": [
                {"id": "a", "role": "card", "x": 10, "y": 10, "width": 100, "height": 80}
            ],
        }
        patch = {
            "operations": [
                {"op": "move_resize", "node_id": "a", "x": 24, "y": 32, "width": 180, "height": 96}
            ]
        }
        repaired = apply_patch_to_canvas(canvas, patch)
        self.assertEqual(repaired["nodes"][0]["x"], 24)
        self.assertEqual(repaired["nodes"][0]["y"], 32)
        self.assertEqual(repaired["nodes"][0]["width"], 180)
        self.assertEqual(repaired["nodes"][0]["height"], 96)

    def test_group_writes_group_metadata(self):
        canvas = {
            "frame": {"id": "test", "width": 400, "height": 300},
            "nodes": [
                {"id": "a", "role": "image", "x": 10, "y": 10, "width": 100, "height": 80},
                {"id": "b", "role": "caption", "x": 10, "y": 100, "width": 100, "height": 24},
            ],
        }
        patch = {
            "operations": [
                {
                    "op": "group",
                    "group_id": "group_figure",
                    "node_ids": ["a", "b"],
                    "metadata": {"role": "figure"},
                }
            ]
        }
        repaired = apply_patch_to_canvas(canvas, patch)
        self.assertEqual(repaired["groups"][0]["id"], "group_figure")
        self.assertEqual(repaired["nodes"][0]["group_id"], "group_figure")
        self.assertEqual(repaired["groups"][0]["metadata"]["role"], "figure")

    def test_snap_to_grid_rounds_geometry(self):
        canvas = {
            "frame": {"id": "test", "width": 400, "height": 300},
            "nodes": [
                {"id": "a", "role": "card", "x": 13, "y": 21, "width": 103, "height": 77}
            ],
        }
        patch = {"operations": [{"op": "snap_to_grid", "node_ids": ["a"], "grid_size": 8}]}
        repaired = apply_patch_to_canvas(canvas, patch)
        self.assertEqual(repaired["nodes"][0]["x"], 16)
        self.assertEqual(repaired["nodes"][0]["y"], 24)
        self.assertEqual(repaired["nodes"][0]["width"], 104)
        self.assertEqual(repaired["nodes"][0]["height"], 80)

    def test_pair_caption_image_positions_and_groups_caption(self):
        canvas = {
            "frame": {"id": "test", "width": 400, "height": 300},
            "nodes": [
                {"id": "image", "role": "image", "x": 80, "y": 40, "width": 200, "height": 120},
                {"id": "caption", "role": "caption", "x": 20, "y": 220, "width": 120, "height": 24},
            ],
        }
        patch = {
            "operations": [
                {"op": "pair_caption_image", "image_id": "image", "caption_id": "caption", "gap": 24}
            ]
        }
        repaired = apply_patch_to_canvas(canvas, patch)
        caption = repaired["nodes"][1]
        self.assertEqual(caption["x"], 80)
        self.assertEqual(caption["y"], 184)
        self.assertEqual(caption["width"], 200)
        self.assertEqual(repaired["groups"][0]["metadata"]["role"], "image_caption_pair")

    def test_define_region_and_route_connectors_write_metadata(self):
        canvas = {
            "frame": {"id": "test", "width": 400, "height": 300},
            "nodes": [
                {"id": "step_01", "role": "process_step", "x": 20, "y": 100, "width": 80, "height": 60},
                {"id": "line_01", "role": "connector", "x": 0, "y": 0, "width": 1, "height": 1},
            ],
        }
        patch = {
            "operations": [
                {
                    "op": "define_region",
                    "region_id": "middle_process",
                    "role": "process_row",
                    "node_ids": ["step_01"],
                    "x": 20,
                    "y": 90,
                    "width": 200,
                    "height": 90,
                },
                {
                    "op": "route_connectors",
                    "connector_ids": ["line_01"],
                    "style": "orthogonal",
                    "avoid_node_ids": ["step_01"],
                },
            ]
        }
        repaired = apply_patch_to_canvas(canvas, patch)
        self.assertEqual(repaired["layout_metadata"]["regions"]["middle_process"]["role"], "process_row")
        self.assertEqual(
            repaired["layout_metadata"]["connector_routes"]["line_01"]["avoid_node_ids"],
            ["step_01"],
        )

    def test_forbidden_operations_are_rejected(self):
        canvas = {
            "frame": {"id": "test", "width": 400, "height": 300},
            "nodes": [{"id": "a", "role": "text", "x": 0, "y": 0, "width": 100, "height": 40}],
        }
        for op in ("delete_content", "rewrite_text", "replace_image", "change_brand_style", "flatten_editable_layers"):
            with self.assertRaises(ValueError):
                apply_patch_to_canvas(canvas, {"operations": [{"op": op, "node_id": "a"}]})


if __name__ == "__main__":
    unittest.main()
