#!/usr/bin/env python3
"""Apply a Frame Doctor layout patch to a canvas JSON file."""

import argparse
import copy
import json
import sys

FORBIDDEN_OPERATIONS = {
    "delete_content",
    "rewrite_text",
    "replace_image",
    "change_brand_style",
    "flatten_editable_layers",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def node_index(canvas):
    return {node.get("id"): node for node in canvas.get("nodes", [])}


def group_bounds(nodes):
    left = min(node.get("x", 0) for node in nodes)
    top = min(node.get("y", 0) for node in nodes)
    right = max(node.get("x", 0) + node.get("width", 0) for node in nodes)
    bottom = max(node.get("y", 0) + node.get("height", 0) for node in nodes)
    return {"x": left, "y": top, "width": right - left, "height": bottom - top}


def apply_patch_to_canvas(canvas, patch):
    repaired = copy.deepcopy(canvas)
    nodes = node_index(repaired)
    repaired.setdefault("groups", [])
    repaired.setdefault("layout_metadata", {})

    for operation in patch.get("operations", []):
        op = operation.get("op")
        if op in FORBIDDEN_OPERATIONS:
            raise ValueError(f"Forbidden operation: {op}")

        if op == "move_resize":
            node = nodes.get(operation.get("node_id"))
            if not node:
                continue
            for key in ("x", "y", "width", "height"):
                if key in operation:
                    node[key] = operation[key]

        elif op == "resize_text_box":
            node = nodes.get(operation.get("node_id"))
            if not node:
                continue
            if "width" in operation:
                node["width"] = operation["width"]
            if "height" in operation:
                node["height"] = operation["height"]

        elif op == "group":
            node_ids = operation.get("node_ids", [])
            members = [nodes[node_id] for node_id in node_ids if node_id in nodes]
            for member in members:
                member["group_id"] = operation.get("group_id")
            group_record = {
                "id": operation.get("group_id"),
                "node_ids": node_ids,
                "metadata": operation.get("metadata", {}),
            }
            if members:
                group_record.update(group_bounds(members))
            repaired["groups"] = [g for g in repaired["groups"] if g.get("id") != group_record["id"]]
            repaired["groups"].append(group_record)

        elif op == "ungroup":
            group_id = operation.get("group_id")
            repaired["groups"] = [group for group in repaired["groups"] if group.get("id") != group_id]
            for node in repaired.get("nodes", []):
                if node.get("group_id") == group_id:
                    node.pop("group_id", None)

        elif op == "apply_auto_layout":
            auto_layout = repaired["layout_metadata"].setdefault("auto_layout", {})
            auto_layout[operation.get("target_id")] = {
                "direction": operation.get("direction"),
                "spacing": operation.get("spacing"),
                "padding": operation.get("padding"),
            }

        elif op == "set_constraints":
            node = nodes.get(operation.get("node_id"))
            if not node:
                continue
            node["constraints"] = {
                "horizontal": operation.get("horizontal"),
                "vertical": operation.get("vertical"),
            }

        elif op == "normalize_spacing":
            normalize_spacing(repaired, operation)

        elif op == "align_edges":
            align_edges(repaired, operation)

        elif op == "snap_to_grid":
            snap_to_grid(repaired, operation)

        elif op == "pair_caption_image":
            pair_caption_image(repaired, operation)

        elif op == "define_region":
            define_region(repaired, operation)

        elif op == "route_connectors":
            route_connectors(repaired, operation)

        else:
            raise ValueError(f"Unsupported operation: {op}")

    return repaired


def normalize_spacing(canvas, operation):
    nodes = node_index(canvas)
    selected = [nodes[node_id] for node_id in operation.get("node_ids", []) if node_id in nodes]
    axis = operation.get("axis", "x")
    spacing = operation.get("spacing", 24)
    selected.sort(key=lambda node: node.get(axis, 0))
    cursor = None
    for node in selected:
        if cursor is None:
            cursor = node.get(axis, 0) + node.get("width" if axis == "x" else "height", 0)
            continue
        node[axis] = cursor + spacing
        cursor = node[axis] + node.get("width" if axis == "x" else "height", 0)


def align_edges(canvas, operation):
    nodes = node_index(canvas)
    selected = [nodes[node_id] for node_id in operation.get("node_ids", []) if node_id in nodes]
    if not selected:
        return
    edge = operation.get("edge", "top")
    if edge == "left":
        value = min(node.get("x", 0) for node in selected)
        for node in selected:
            node["x"] = value
    elif edge == "right":
        value = max(node.get("x", 0) + node.get("width", 0) for node in selected)
        for node in selected:
            node["x"] = value - node.get("width", 0)
    elif edge == "bottom":
        value = max(node.get("y", 0) + node.get("height", 0) for node in selected)
        for node in selected:
            node["y"] = value - node.get("height", 0)
    else:
        value = min(node.get("y", 0) for node in selected)
        for node in selected:
            node["y"] = value


def snap_to_grid(canvas, operation):
    nodes = node_index(canvas)
    grid_size = max(float(operation.get("grid_size", 8)), 1.0)
    for node_id in operation.get("node_ids", []):
        node = nodes.get(node_id)
        if not node:
            continue
        for key in ("x", "y", "width", "height"):
            node[key] = int(round(float(node.get(key, 0)) / grid_size) * grid_size)


def pair_caption_image(canvas, operation):
    nodes = node_index(canvas)
    image = nodes.get(operation.get("image_id"))
    caption = nodes.get(operation.get("caption_id"))
    if not image or not caption:
        return
    gap = operation.get("gap", 24)
    align = operation.get("align", "left")
    if align == "right":
        caption["x"] = image.get("x", 0) + image.get("width", 0) - caption.get("width", 0)
    elif align == "center":
        caption["x"] = image.get("x", 0) + (image.get("width", 0) - caption.get("width", 0)) / 2
    else:
        caption["x"] = image.get("x", 0)
    caption["y"] = image.get("y", 0) + image.get("height", 0) + gap
    caption["width"] = operation.get("width", image.get("width", caption.get("width", 0)))
    group_id = operation.get("group_id", f"group_{image.get('id')}_{caption.get('id')}")
    image["group_id"] = group_id
    caption["group_id"] = group_id
    group_record = {
        "id": group_id,
        "node_ids": [image.get("id"), caption.get("id")],
        "metadata": {"role": "image_caption_pair"},
    }
    group_record.update(group_bounds([image, caption]))
    canvas.setdefault("groups", [])
    canvas["groups"] = [group for group in canvas["groups"] if group.get("id") != group_id]
    canvas["groups"].append(group_record)


def define_region(canvas, operation):
    regions = canvas.setdefault("layout_metadata", {}).setdefault("regions", {})
    region_id = operation.get("region_id")
    if not region_id:
        return
    regions[region_id] = {
        "role": operation.get("role"),
        "node_ids": operation.get("node_ids", []),
        "x": operation.get("x"),
        "y": operation.get("y"),
        "width": operation.get("width"),
        "height": operation.get("height"),
    }


def route_connectors(canvas, operation):
    routes = canvas.setdefault("layout_metadata", {}).setdefault("connector_routes", {})
    route_record = {
        "style": operation.get("style", "orthogonal"),
        "avoid_node_ids": operation.get("avoid_node_ids", []),
        "metadata": operation.get("metadata", {}),
    }
    for connector_id in operation.get("connector_ids", []):
        routes[connector_id] = dict(route_record)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply a Frame Doctor patch to canvas JSON.")
    parser.add_argument("canvas_json", help="Path to a canvas JSON file.")
    parser.add_argument("patch_json", help="Path to a patch JSON file or proposal JSON with recommended_patch.")
    parser.add_argument("--output", required=True, help="Path for repaired canvas JSON.")
    args = parser.parse_args(argv)

    canvas = load_json(args.canvas_json)
    patch_file = load_json(args.patch_json)
    patch = patch_file.get("recommended_patch", patch_file)
    repaired = apply_patch_to_canvas(canvas, patch)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(repaired, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


if __name__ == "__main__":
    main()
