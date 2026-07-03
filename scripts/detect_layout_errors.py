#!/usr/bin/env python3
"""Detect objective layout errors in a Frame Doctor canvas JSON file."""

import argparse
import itertools
import json
import sys


REPEATED_ROLES = {
    "card",
    "kpi_card",
    "settings_row",
    "article_card",
    "product_card",
    "chat_row",
    "health_metric_card",
    "service_grid",
    "result_card",
    "process_step",
}


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


def _role_groups(canvas, min_count=3):
    groups = {}
    for node in _detectable_nodes(canvas):
        role = node.get("role")
        if role in REPEATED_ROLES:
            groups.setdefault(role, []).append(node)
    return {role: nodes for role, nodes in groups.items() if len(nodes) >= min_count}


def detect_alignment_drift(canvas, tolerance=8):
    errors = []
    for role, nodes in _role_groups(canvas).items():
        rects = [(node, rect(node)) for node in nodes]
        tops = [item[1]["top"] for item in rects]
        lefts = [item[1]["left"] for item in rects]
        centers_x = [item[1]["left"] + item[1]["width"] / 2 for item in rects]
        centers_y = [item[1]["top"] + item[1]["height"] / 2 for item in rects]

        row_drift = max(tops) - min(tops)
        column_drift = max(lefts) - min(lefts)
        if row_drift > tolerance and row_drift <= max(item[1]["height"] for item in rects) * 0.45:
            expected = sorted(tops)[len(tops) // 2]
            errors.append(
                {
                    "type": "alignment_drift",
                    "severity": "warning",
                    "nodes": [node.get("id") for node in nodes],
                    "message": "Repeated nodes appear to share a row but their top edges drift.",
                    "metrics": {
                        "role": role,
                        "expected_edge": round(expected, 2),
                        "max_drift": round(row_drift, 2),
                        "axis": "y",
                    },
                }
            )
        if column_drift > tolerance and column_drift <= max(item[1]["width"] for item in rects) * 0.45:
            expected = sorted(lefts)[len(lefts) // 2]
            errors.append(
                {
                    "type": "alignment_drift",
                    "severity": "warning",
                    "nodes": [node.get("id") for node in nodes],
                    "message": "Repeated nodes appear to share a column but their left edges drift.",
                    "metrics": {
                        "role": role,
                        "expected_edge": round(expected, 2),
                        "max_drift": round(column_drift, 2),
                        "axis": "x",
                    },
                }
            )

        center_x_drift = max(centers_x) - min(centers_x)
        center_y_drift = max(centers_y) - min(centers_y)
        if center_x_drift <= tolerance or center_y_drift <= tolerance:
            continue
    return errors


def _sorted_gaps(nodes, axis):
    key = "x" if axis == "x" else "y"
    size = "width" if axis == "x" else "height"
    ordered = sorted(nodes, key=lambda node: float(node.get(key, 0)))
    gaps = []
    for current, following in zip(ordered, ordered[1:]):
        current_end = float(current.get(key, 0)) + float(current.get(size, 0))
        gaps.append(float(following.get(key, 0)) - current_end)
    return gaps


def detect_gutter_anomalies(canvas, min_gap=12, variance_threshold=20):
    errors = []
    for role, nodes in _role_groups(canvas).items():
        for axis in ("x", "y"):
            gaps = [gap for gap in _sorted_gaps(nodes, axis) if gap >= 0]
            if len(gaps) < 2:
                continue
            mean_gap = sum(gaps) / len(gaps)
            deviations = [abs(gap - mean_gap) for gap in gaps]
            max_deviation = max(deviations)
            if max_deviation > variance_threshold or any(0 <= gap < min_gap for gap in gaps):
                errors.append(
                    {
                        "type": "gutter_anomaly",
                        "severity": "warning",
                        "nodes": [node.get("id") for node in nodes],
                        "message": "Repeated nodes have inconsistent gutters or a gutter below minimum.",
                        "metrics": {
                            "role": role,
                            "axis": axis,
                            "gaps": [round(gap, 2) for gap in gaps],
                            "mean_gap": round(mean_gap, 2),
                            "max_deviation": round(max_deviation, 2),
                        },
                    }
                )
    return errors


def _declared_columns(canvas):
    metadata = canvas.get("layout_metadata", {})
    columns = metadata.get("columns") or metadata.get("grid_columns") or []
    anchors = []
    for column in columns:
        if isinstance(column, dict):
            if "x" in column:
                anchors.append(float(column["x"]))
            elif "left" in column:
                anchors.append(float(column["left"]))
        else:
            try:
                anchors.append(float(column))
            except (TypeError, ValueError):
                pass
    return anchors


def detect_column_drift(canvas, tolerance=10):
    errors = []
    anchors = _declared_columns(canvas)
    nodes = _detectable_nodes(canvas)
    if not anchors:
        for role, role_nodes in _role_groups(canvas).items():
            lefts = sorted(round(rect(node)["left"], 1) for node in role_nodes)
            if max(lefts) - min(lefts) <= 48:
                anchors.append(sorted(lefts)[len(lefts) // 2])
    if not anchors:
        return []

    for node in nodes:
        r = rect(node)
        nearest = min(anchors, key=lambda anchor: abs(anchor - r["left"]))
        drift = abs(nearest - r["left"])
        if drift > tolerance and drift <= 64:
            errors.append(
                {
                    "type": "column_drift",
                    "severity": "warning",
                    "nodes": [node.get("id")],
                    "message": "Node edge drifts from an expected column anchor.",
                    "metrics": {
                        "expected_column_x": round(nearest, 2),
                        "actual_x": round(r["left"], 2),
                        "drift": round(drift, 2),
                    },
                }
            )
    return errors


def _baseline_value(node):
    metadata = node.get("metadata", {})
    if "baseline" in node:
        return float(node["baseline"])
    if "baseline" in metadata:
        return float(metadata["baseline"])
    return rect(node)["top"]


def detect_baseline_mismatch(canvas):
    metadata = canvas.get("layout_metadata", {})
    baseline_grid = metadata.get("baseline_grid")
    if isinstance(baseline_grid, dict):
        interval = baseline_grid.get("interval") or baseline_grid.get("size")
    else:
        interval = baseline_grid
    if interval is None:
        return []
    interval = float(interval)
    if interval <= 0:
        return []

    errors = []
    for node in _detectable_nodes(canvas):
        if node.get("type") != "text":
            continue
        baseline = _baseline_value(node)
        offset = baseline % interval
        offset = min(offset, interval - offset)
        if offset > 1.5:
            errors.append(
                {
                    "type": "baseline_mismatch",
                    "severity": "warning",
                    "nodes": [node.get("id")],
                    "message": "Text baseline does not align to the declared baseline grid.",
                    "metrics": {"baseline_grid": round(interval, 2), "offset": round(offset, 2)},
                }
            )
    return errors


def _font_size(node):
    for key in ("font_size", "fontSize", "text_size"):
        if key in node:
            return float(node[key])
    metadata = node.get("metadata", {})
    for key in ("font_size", "fontSize", "text_size"):
        if key in metadata:
            return float(metadata[key])
    role = node.get("role")
    if role == "title":
        return min(float(node.get("height", 40)), 64.0)
    if role == "subtitle":
        return min(float(node.get("height", 28)), 32.0)
    if node.get("type") == "text" or role == "body":
        return 20.0
    return float(node.get("height", 0))


def detect_hierarchy_ambiguity(canvas):
    text_nodes = [node for node in _detectable_nodes(canvas) if node.get("type") == "text" or node.get("role") in ("title", "subtitle", "body")]
    errors = []
    title_nodes = [node for node in text_nodes if node.get("role") == "title" or "title" in str(node.get("id", "")).lower()]
    large_text = [node for node in text_nodes if _font_size(node) >= 32 or node.get("role") == "title"]
    if len(large_text) >= 2:
        sizes = [_font_size(node) for node in large_text]
        if max(sizes) / max(min(sizes), 1.0) < 1.25:
            errors.append(
                {
                    "type": "hierarchy_ambiguity",
                    "severity": "uncertain",
                    "nodes": [node.get("id") for node in large_text[:4]],
                    "message": "Multiple title-like text nodes compete for primary hierarchy.",
                    "metrics": {
                        "competing_nodes": [node.get("id") for node in large_text[:4]],
                        "size_ratio": round(max(sizes) / max(min(sizes), 1.0), 2),
                    },
                }
            )
    if title_nodes:
        title_size = max(_font_size(node) for node in title_nodes)
        body_like = [node for node in text_nodes if node.get("role") in ("body", "card", "article_card")]
        if body_like:
            body_size = max(_font_size(node) for node in body_like)
            if title_size < body_size:
                errors.append(
                    {
                        "type": "hierarchy_ambiguity",
                        "severity": "warning",
                        "nodes": [title_nodes[0].get("id"), body_like[0].get("id")],
                        "message": "Primary title appears smaller than body or card text.",
                        "metrics": {"title_size": round(title_size, 2), "body_size": round(body_size, 2)},
                    }
                )
    return errors


def summarize(errors):
    summary = {
        "error_count": len(errors),
        "critical_count": 0,
        "warning_count": 0,
        "uncertain_count": 0,
        "total_overlap_area": 0.0,
        "total_overflow_distance": 0.0,
        "total_spacing_violations": 0,
        "total_alignment_drift": 0.0,
        "total_gutter_anomaly": 0,
        "total_grid_snap_error": 0.0,
    }
    for error in errors:
        key = f"{error.get('severity')}_count"
        if key in summary:
            summary[key] += 1
        type_key = f"{error.get('type')}_count"
        summary[type_key] = summary.get(type_key, 0) + 1
        metrics = error.get("metrics", {})
        if error.get("type") == "overlap":
            summary["total_overlap_area"] += float(metrics.get("overlap_area", 0))
        elif error.get("type") in ("out_of_bounds", "text_overflow", "margin_breach"):
            summary["total_overflow_distance"] += sum(
                float(value) for value in metrics.values() if isinstance(value, (int, float))
            )
        elif error.get("type") == "spacing_violation":
            summary["total_spacing_violations"] += 1
        elif error.get("type") == "alignment_drift":
            summary["total_alignment_drift"] += float(metrics.get("max_drift", 0))
        elif error.get("type") == "gutter_anomaly":
            summary["total_gutter_anomaly"] += 1
        elif error.get("type") == "column_drift":
            summary["total_grid_snap_error"] += float(metrics.get("drift", 0))
    for key, value in list(summary.items()):
        if isinstance(value, float):
            summary[key] = round(value, 2)
    return summary


def detect_layout_errors(canvas):
    errors = []
    errors.extend(detect_overlaps(canvas))
    errors.extend(detect_out_of_bounds(canvas))
    errors.extend(detect_margin_breaches(canvas))
    errors.extend(detect_spacing_violations(canvas))
    errors.extend(detect_text_overflows(canvas))
    errors.extend(detect_image_caption_detachment(canvas))
    errors.extend(detect_alignment_drift(canvas))
    errors.extend(detect_gutter_anomalies(canvas))
    errors.extend(detect_column_drift(canvas))
    errors.extend(detect_baseline_mismatch(canvas))
    errors.extend(detect_hierarchy_ambiguity(canvas))
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
