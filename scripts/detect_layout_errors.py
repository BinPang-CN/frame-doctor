#!/usr/bin/env python3
"""Detect objective layout errors in a Frame Doctor canvas JSON file."""

import argparse
import itertools
import json
import sys


def load_canvas(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def rect(node):
    return {
        "left": float(node.get("x", 0)),
        "top": float(node.get("y", 0)),
        "right": float(node.get("x", 0)) + float(node.get("width", 0)),
        "bottom": float(node.get("y", 0)) + float(node.get("height", 0)),
        "width": float(node.get("width", 0)),
        "height": float(node.get("height", 0)),
    }


def _detectable_nodes(canvas):
    return [
        node
        for node in canvas.get("nodes", [])
        if node.get("type") != "group" and node.get("visible", True)
    ]


def overlap_area(a, b):
    ra = rect(a)
    rb = rect(b)
    width = max(0.0, min(ra["right"], rb["right"]) - max(ra["left"], rb["left"]))
    height = max(0.0, min(ra["bottom"], rb["bottom"]) - max(ra["top"], rb["top"]))
    return width * height


def detect_overlaps(canvas):
    errors = []
    for a, b in itertools.combinations(_detectable_nodes(canvas), 2):
        area = overlap_area(a, b)
        if area > 0:
            errors.append(
                {
                    "type": "overlap",
                    "severity": "critical",
                    "nodes": [a.get("id"), b.get("id")],
                    "message": "Nodes overlap and may block content.",
                    "metrics": {"overlap_area": round(area, 2)},
                }
            )
    return errors


def detect_out_of_bounds(canvas):
    frame = canvas.get("frame", {})
    frame_width = float(frame.get("width", 0))
    frame_height = float(frame.get("height", 0))
    errors = []
    for node in _detectable_nodes(canvas):
        r = rect(node)
        overflow_left = max(0.0, -r["left"])
        overflow_top = max(0.0, -r["top"])
        overflow_right = max(0.0, r["right"] - frame_width)
        overflow_bottom = max(0.0, r["bottom"] - frame_height)
        overflow = overflow_left + overflow_top + overflow_right + overflow_bottom
        if overflow > 0:
            errors.append(
                {
                    "type": "out_of_bounds",
                    "severity": "critical",
                    "nodes": [node.get("id")],
                    "message": "Node extends beyond the frame bounds.",
                    "metrics": {
                        "left": round(overflow_left, 2),
                        "top": round(overflow_top, 2),
                        "right": round(overflow_right, 2),
                        "bottom": round(overflow_bottom, 2),
                    },
                }
            )
    return errors


def detect_margin_breaches(canvas):
    frame = canvas.get("frame", {})
    safe_margin = frame.get("safe_margin")
    if safe_margin is None:
        safe_margin = canvas.get("layout_metadata", {}).get("safe_margin")
    if safe_margin is None:
        return []

    margin = float(safe_margin)
    frame_width = float(frame.get("width", 0))
    frame_height = float(frame.get("height", 0))
    errors = []
    for node in _detectable_nodes(canvas):
        r = rect(node)
        breaches = {
            "left": max(0.0, margin - r["left"]),
            "top": max(0.0, margin - r["top"]),
            "right": max(0.0, r["right"] - (frame_width - margin)),
            "bottom": max(0.0, r["bottom"] - (frame_height - margin)),
        }
        if sum(breaches.values()) > 0:
            errors.append(
                {
                    "type": "margin_breach",
                    "severity": "warning",
                    "nodes": [node.get("id")],
                    "message": "Node violates the declared safe margin or type area.",
                    "metrics": {key: round(value, 2) for key, value in breaches.items()},
                }
            )
    return errors


def detect_spacing_violations(canvas, min_spacing=24):
    errors = []
    for a, b in itertools.combinations(_detectable_nodes(canvas), 2):
        if overlap_area(a, b) > 0:
            continue

        ra = rect(a)
        rb = rect(b)
        vertical_overlap = min(ra["bottom"], rb["bottom"]) - max(ra["top"], rb["top"])
        horizontal_overlap = min(ra["right"], rb["right"]) - max(ra["left"], rb["left"])

        if vertical_overlap > 0:
            gap = max(rb["left"] - ra["right"], ra["left"] - rb["right"])
            if 0 < gap < min_spacing:
                errors.append(
                    {
                        "type": "spacing_violation",
                        "severity": "warning",
                        "nodes": [a.get("id"), b.get("id")],
                        "message": "Horizontal gap is below the minimum spacing.",
                        "metrics": {"axis": "x", "gap": round(gap, 2), "minimum": min_spacing},
                    }
                )

        if horizontal_overlap > 0:
            gap = max(rb["top"] - ra["bottom"], ra["top"] - rb["bottom"])
            if 0 < gap < min_spacing:
                errors.append(
                    {
                        "type": "spacing_violation",
                        "severity": "warning",
                        "nodes": [a.get("id"), b.get("id")],
                        "message": "Vertical gap is below the minimum spacing.",
                        "metrics": {"axis": "y", "gap": round(gap, 2), "minimum": min_spacing},
                    }
                )
    return errors


def detect_text_overflows(canvas):
    errors = []
    for node in _detectable_nodes(canvas):
        if node.get("type") != "text" or not node.get("text"):
            continue
        width = max(float(node.get("width", 0)), 1.0)
        height = max(float(node.get("height", 0)), 1.0)
        chars_per_line = max(int(width / 8), 1)
        line_count = (len(node.get("text", "")) + chars_per_line - 1) // chars_per_line
        needed_height = line_count * 20
        if needed_height > height * 1.15:
            errors.append(
                {
                    "type": "text_overflow",
                    "severity": "critical",
                    "nodes": [node.get("id")],
                    "message": "Text likely exceeds the available text box height.",
                    "metrics": {
                        "estimated_height": round(needed_height, 2),
                        "box_height": round(height, 2),
                    },
                }
            )
    return errors


def detect_semantic_role_uncertainty(canvas):
    errors = []
    for node in _detectable_nodes(canvas):
        role = node.get("role")
        if not role or role == "unknown":
            errors.append(
                {
                    "type": "semantic_role_uncertainty",
                    "severity": "uncertain",
                    "nodes": [node.get("id")],
                    "message": "Node role is missing or uncertain.",
                    "metrics": {},
                }
            )
    return errors


def detect_image_caption_detachment(canvas, max_gap=96):
    images = [
        node
        for node in _detectable_nodes(canvas)
        if node.get("role") in ("image", "chart") or node.get("type") in ("image", "chart")
    ]
    captions = [node for node in _detectable_nodes(canvas) if node.get("role") == "caption"]
    errors = []
    for caption in captions:
        if not images:
            continue
        caption_rect = rect(caption)
        best = None
        best_gap = None
        for image in images:
            image_rect = rect(image)
            vertical_gap = caption_rect["top"] - image_rect["bottom"]
            horizontal_overlap = min(caption_rect["right"], image_rect["right"]) - max(caption_rect["left"], image_rect["left"])
            if vertical_gap >= 0 and horizontal_overlap > 0:
                if best_gap is None or vertical_gap < best_gap:
                    best = image
                    best_gap = vertical_gap
        if best is None or best_gap is None:
            continue
        image_rect = rect(best)
        left_drift = abs(caption_rect["left"] - image_rect["left"])
        if best_gap > max_gap or left_drift > 24:
            errors.append(
                {
                    "type": "image_caption_detachment",
                    "severity": "warning",
                    "nodes": [best.get("id"), caption.get("id")],
                    "message": "Caption is detached from or misaligned with its image/chart.",
                    "metrics": {"gap": round(best_gap, 2), "left_drift": round(left_drift, 2)},
                }
            )
    return errors


def summarize(errors):
    summary = {
        "error_count": len(errors),
        "critical_count": 0,
        "warning_count": 0,
        "uncertain_count": 0,
    }
    for error in errors:
        key = f"{error.get('severity')}_count"
        if key in summary:
            summary[key] += 1
        type_key = f"{error.get('type')}_count"
        summary[type_key] = summary.get(type_key, 0) + 1
    return summary


def detect_layout_errors(canvas):
    errors = []
    errors.extend(detect_overlaps(canvas))
    errors.extend(detect_out_of_bounds(canvas))
    errors.extend(detect_margin_breaches(canvas))
    errors.extend(detect_spacing_violations(canvas))
    errors.extend(detect_text_overflows(canvas))
    errors.extend(detect_image_caption_detachment(canvas))
    errors.extend(detect_semantic_role_uncertainty(canvas))
    return {"errors": errors, "summary": summarize(errors)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Detect Frame Doctor layout errors.")
    parser.add_argument("canvas_json", help="Path to a canvas JSON file.")
    args = parser.parse_args(argv)

    canvas = load_canvas(args.canvas_json)
    json.dump(detect_layout_errors(canvas), sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
