#!/usr/bin/env python3
"""Score a Frame Doctor canvas JSON file."""

import argparse
import json
import sys

try:
    from detect_layout_errors import detect_layout_errors, load_canvas
except ModuleNotFoundError:
    from scripts.detect_layout_errors import detect_layout_errors, load_canvas


def score_layout(canvas):
    report = detect_layout_errors(canvas)
    summary = report["summary"]
    overlap_count = summary.get("overlap_count", 0)
    out_of_bounds_count = summary.get("out_of_bounds_count", 0)
    spacing_violation_count = summary.get("spacing_violation_count", 0)
    text_overflow_count = summary.get("text_overflow_count", 0)
    margin_breach_count = summary.get("margin_breach_count", 0)
    image_caption_detachment_count = summary.get("image_caption_detachment_count", 0)
    alignment_drift_count = summary.get("alignment_drift_count", 0)
    gutter_anomaly_count = summary.get("gutter_anomaly_count", 0)
    column_drift_count = summary.get("column_drift_count", 0)
    baseline_mismatch_count = summary.get("baseline_mismatch_count", 0)
    hierarchy_ambiguity_count = summary.get("hierarchy_ambiguity_count", 0)
    uncertain_count = summary.get("semantic_role_uncertainty_count", 0)

    penalty = (
        overlap_count * 20
        + out_of_bounds_count * 18
        + text_overflow_count * 16
        + margin_breach_count * 4
        + spacing_violation_count * 5
        + image_caption_detachment_count * 5
        + alignment_drift_count * 4
        + gutter_anomaly_count * 4
        + column_drift_count * 3
        + baseline_mismatch_count * 3
        + hierarchy_ambiguity_count * 5
        + uncertain_count * 2
    )
    score = max(0, 100 - penalty)

    return {
        "score": score,
        "overlap_count": overlap_count,
        "out_of_bounds_count": out_of_bounds_count,
        "spacing_violation_count": spacing_violation_count,
        "text_overflow_count": text_overflow_count,
        "margin_breach_count": margin_breach_count,
        "image_caption_detachment_count": image_caption_detachment_count,
        "alignment_drift_count": alignment_drift_count,
        "gutter_anomaly_count": gutter_anomaly_count,
        "column_drift_count": column_drift_count,
        "baseline_mismatch_count": baseline_mismatch_count,
        "hierarchy_ambiguity_count": hierarchy_ambiguity_count,
        "error_count": summary.get("error_count", 0),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Score a Frame Doctor canvas JSON file.")
    parser.add_argument("canvas_json", help="Path to a canvas JSON file.")
    args = parser.parse_args(argv)

    canvas = load_canvas(args.canvas_json)
    json.dump(score_layout(canvas), sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
