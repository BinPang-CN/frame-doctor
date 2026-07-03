#!/usr/bin/env python3
"""Run the full Frame Doctor JSON MVP loop and print a Markdown report."""

import argparse
import json

from apply_patch_to_json import apply_patch_to_canvas
from detect_layout_errors import load_canvas
from propose_layout_patch import load_profile, propose_layout_patch
from score_layout import score_layout


def compact_errors(report):
    lines = []
    for error in report.get("errors", []):
        nodes = ", ".join(str(node) for node in error.get("nodes", []))
        lines.append(f"- {error['severity']} `{error['type']}` on {nodes}: {error['message']}")
    return lines or ["- No layout conflicts detected."]


def run_demo(canvas_path, profile_path):
    canvas = load_canvas(canvas_path)
    profile = load_profile(profile_path)
    before_score = score_layout(canvas)
    proposal = propose_layout_patch(canvas, profile)
    repaired = apply_patch_to_canvas(canvas, proposal["recommended_patch"])
    after_score = score_layout(repaired)
    after_conflicts = proposal["layout_conflict_report"]
    repaired_report = propose_layout_patch(repaired, profile)["layout_conflict_report"]

    print("# Frame Doctor Demo Report")
    print()
    print(f"- Canvas: `{canvas_path}`")
    print(f"- Profile: `{profile_path}`")
    print(f"- Recommended pattern: `{proposal['recommended_patch']['pattern']}`")
    print(f"- Score before: {before_score['score']}")
    print(f"- Score after: {after_score['score']}")
    print()
    print("## Layout Conflict Report")
    print()
    for line in compact_errors(after_conflicts):
        print(line)
    print()
    print("## Semantic Role Map")
    print()
    for item in proposal["semantic_role_map"]:
        print(f"- `{item['node_id']}` -> `{item['role']}` ({item['confidence']:.2f})")
    print()
    print("## Structure Candidates")
    print()
    for candidate in proposal["structure_candidates"]:
        print(f"- `{candidate['pattern']}` ({candidate['confidence']:.2f}): {candidate['reason']}")
    print()
    print("## Human Value Profile")
    print()
    print("```json")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    print("```")
    print()
    print("## Layout Patch")
    print()
    print("```json")
    print(json.dumps(proposal["recommended_patch"], indent=2, ensure_ascii=False))
    print("```")
    print()
    print("## Layout QA Report")
    print()
    print("Before:")
    print("```json")
    print(json.dumps(before_score, indent=2, ensure_ascii=False))
    print("```")
    print("After:")
    print("```json")
    print(json.dumps(after_score, indent=2, ensure_ascii=False))
    print("```")
    print("Remaining conflicts:")
    for line in compact_errors(repaired_report):
        print(line)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run Frame Doctor demo.")
    parser.add_argument("canvas_json", help="Path to a canvas JSON file.")
    parser.add_argument("--profile", required=True, help="Path to a value profile JSON file.")
    args = parser.parse_args(argv)
    run_demo(args.canvas_json, args.profile)


if __name__ == "__main__":
    main()
