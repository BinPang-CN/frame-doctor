#!/usr/bin/env python3
"""Compare before/after canvases for the LDS L4 audit loop."""

import argparse
import json

try:
    from detect_layout_errors import detect_layout_errors, load_canvas, overlap_area
    from score_layout import score_layout
except ModuleNotFoundError:
    from scripts.detect_layout_errors import detect_layout_errors, load_canvas, overlap_area
    from scripts.score_layout import score_layout


def _nodes(canvas):
    return [node for node in canvas.get("nodes", []) if node.get("visible", True)]


def _node_map(canvas):
    return {node.get("id"): node for node in _nodes(canvas)}


def compute_overlap_area(canvas):
    nodes = _nodes(canvas)
    total = 0.0
    for index, node in enumerate(nodes):
        for other in nodes[index + 1 :]:
            total += overlap_area(node, other)
    return round(total, 2)


def compute_overflow_distance(canvas):
    report = detect_layout_errors(canvas)
    total = 0.0
    for error in report.get("errors", []):
        metrics = error.get("metrics", {})
        if error.get("type") == "text_overflow":
            if "overflow_distance" in metrics:
                total += float(metrics.get("overflow_distance", 0))
            else:
                total += max(
                    0.0,
                    float(metrics.get("estimated_height", 0)) - float(metrics.get("box_height", 0)),
                )
        elif error.get("type") in ("out_of_bounds", "margin_breach"):
            for value in error.get("metrics", {}).values():
                if isinstance(value, (int, float)):
                    total += float(value)
    return round(total, 2)


def compute_alignment_drift(canvas):
    report = detect_layout_errors(canvas)
    total = 0.0
    for error in report.get("errors", []):
        if error.get("type") == "alignment_drift":
            total += float(error.get("metrics", {}).get("max_drift", 0))
    return round(total, 2)


def compute_grid_snap_error(canvas):
    metadata = canvas.get("layout_metadata", {})
    grid_size = metadata.get("grid_size") or metadata.get("grid", {}).get("grid_size")
    if not grid_size:
        baseline = metadata.get("baseline_grid")
        if isinstance(baseline, dict):
            grid_size = baseline.get("interval") or baseline.get("size")
    if not grid_size:
        report = detect_layout_errors(canvas)
        return round(float(report.get("summary", {}).get("total_grid_snap_error", 0)), 2)
    grid_size = max(float(grid_size), 1.0)
    total = 0.0
    for node in _nodes(canvas):
        for key in ("x", "y"):
            value = float(node.get(key, 0))
            offset = value % grid_size
            total += min(offset, grid_size - offset)
    return round(total, 2)


def compute_hierarchy_clarity(canvas):
    report = detect_layout_errors(canvas)
    ambiguity = report.get("summary", {}).get("hierarchy_ambiguity_count", 0)
    title_wrap = report.get("summary", {}).get("title_wrapping_count", 0)
    score = 1.0 - min(1.0, ambiguity * 0.22 + title_wrap * 0.18)
    return round(score, 3)


def compute_layout_stability(before_canvas, after_canvas):
    before = _node_map(before_canvas)
    after = _node_map(after_canvas)
    frame = before_canvas.get("frame", {})
    frame_scale = max(float(frame.get("width", 1)) + float(frame.get("height", 1)), 1.0)
    movement = 0.0
    comparable = 0
    for node_id, before_node in before.items():
        after_node = after.get(node_id)
        if not after_node:
            continue
        comparable += 1
        movement += abs(float(after_node.get("x", 0)) - float(before_node.get("x", 0)))
        movement += abs(float(after_node.get("y", 0)) - float(before_node.get("y", 0)))
        movement += abs(float(after_node.get("width", 0)) - float(before_node.get("width", 0))) * 0.4
        movement += abs(float(after_node.get("height", 0)) - float(before_node.get("height", 0))) * 0.4
    if comparable == 0:
        return 0.0
    normalized = movement / (frame_scale * comparable)
    return round(max(0.0, 1.0 - normalized), 3)


def audit_layout(before_canvas, after_canvas):
    before_score = score_layout(before_canvas)
    after_score = score_layout(after_canvas)
    before_report = detect_layout_errors(before_canvas)
    after_report = detect_layout_errors(after_canvas)

    overlap_before = compute_overlap_area(before_canvas)
    overlap_after = compute_overlap_area(after_canvas)
    overflow_before = compute_overflow_distance(before_canvas)
    overflow_after = compute_overflow_distance(after_canvas)
    alignment_before = compute_alignment_drift(before_canvas)
    alignment_after = compute_alignment_drift(after_canvas)
    grid_before = compute_grid_snap_error(before_canvas)
    grid_after = compute_grid_snap_error(after_canvas)

    human_summary = [
        f"Score changed from {before_score['score']} to {after_score['score']}.",
        f"Critical conflicts changed from {before_report['summary'].get('critical_count', 0)} to {after_report['summary'].get('critical_count', 0)}.",
        f"Overlap area changed from {overlap_before} to {overlap_after}.",
        f"Overflow distance changed from {overflow_before} to {overflow_after}.",
        f"Alignment drift changed from {alignment_before} to {alignment_after}.",
    ]

    return {
        "before_score": before_score["score"],
        "after_score": after_score["score"],
        "score_delta": after_score["score"] - before_score["score"],
        "conflict_reduction": {
            "before_error_count": before_report["summary"].get("error_count", 0),
            "after_error_count": after_report["summary"].get("error_count", 0),
            "before_critical_count": before_report["summary"].get("critical_count", 0),
            "after_critical_count": after_report["summary"].get("critical_count", 0),
        },
        "metric_deltas": {
            "overlap_area_before": overlap_before,
            "overlap_area_after": overlap_after,
            "overlap_area_reduction": round(overlap_before - overlap_after, 2),
            "overflow_distance_before": overflow_before,
            "overflow_distance_after": overflow_after,
            "overflow_distance_reduction": round(overflow_before - overflow_after, 2),
            "alignment_drift_before": alignment_before,
            "alignment_drift_after": alignment_after,
            "alignment_drift_reduction": round(alignment_before - alignment_after, 2),
            "grid_snap_error_before": grid_before,
            "grid_snap_error_after": grid_after,
            "grid_snap_error_reduction": round(grid_before - grid_after, 2),
            "hierarchy_clarity_after": compute_hierarchy_clarity(after_canvas),
            "layout_stability": compute_layout_stability(before_canvas, after_canvas),
        },
        "human_readable_summary": human_summary,
        "remaining_conflicts": after_report.get("errors", []),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit before/after Frame Doctor canvases.")
    parser.add_argument("before_canvas_json", help="Path to the before canvas JSON file.")
    parser.add_argument("after_canvas_json", help="Path to the repaired canvas JSON file.")
    args = parser.parse_args(argv)

    before_canvas = load_canvas(args.before_canvas_json)
    after_canvas = load_canvas(args.after_canvas_json)
    print(json.dumps(audit_layout(before_canvas, after_canvas), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
