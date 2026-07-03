#!/usr/bin/env python3
"""Run the full Frame Doctor JSON MVP loop and print a Markdown report."""

import argparse
import json
import os

try:
    from apply_patch_to_json import apply_patch_to_canvas
    from audit_layout import audit_layout
    from detect_layout_errors import detect_layout_errors, load_canvas
    from propose_layout_patch import load_profile, propose_layout_patch
    from render_canvas_html import render_comparison
except ModuleNotFoundError:
    from scripts.apply_patch_to_json import apply_patch_to_canvas
    from scripts.audit_layout import audit_layout
    from scripts.detect_layout_errors import detect_layout_errors, load_canvas
    from scripts.propose_layout_patch import load_profile, propose_layout_patch
    from scripts.render_canvas_html import render_comparison


VALUE_PROFILE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "value_profiles")
NAMED_VALUE_PROFILES = {
    "readability_first": "readability_first.json",
    "visual_impact_first": "visual_impact_first.json",
    "density_first": "density_first.json",
    "grid_strict": "grid_strict.json",
    "minimal_fix": "minimal_fix.json",
}


def compact_errors(report):
    lines = []
    for error in report.get("errors", []):
        nodes = ", ".join(str(node) for node in error.get("nodes", []))
        lines.append(f"- {error['severity']} `{error['type']}` on {nodes}: {error['message']}")
    return lines or ["- No layout conflicts detected."]


def load_named_value_profile(name):
    if name not in NAMED_VALUE_PROFILES:
        raise ValueError(f"Unknown value profile: {name}")
    return load_profile(os.path.join(VALUE_PROFILE_DIR, NAMED_VALUE_PROFILES[name]))


def candidate_patch_options(proposal):
    return [proposal["recommended_patch"]] + list(proposal.get("alternatives", []))


def select_candidate_patch(proposal, selection):
    options = candidate_patch_options(proposal)
    if not selection or not str(selection).strip():
        return options[0]
    try:
        index = int(str(selection).strip()) - 1
    except ValueError:
        return options[0]
    if 0 <= index < len(options):
        return options[index]
    return options[0]


def patch_operation_summary(patch):
    lines = []
    for index, operation in enumerate(patch.get("operations", []), start=1):
        op = operation.get("op", "unknown")
        if op == "move_resize":
            lines.append(
                f"{index}. move {operation.get('node_id')} to "
                f"x={operation.get('x')} y={operation.get('y')} "
                f"w={operation.get('width')} h={operation.get('height')}"
            )
        elif op == "group":
            lines.append(f"{index}. group {', '.join(operation.get('node_ids', []))} as {operation.get('group_id')}")
        elif op == "apply_auto_layout":
            lines.append(
                f"{index}. apply {operation.get('direction')} auto layout to {operation.get('target_id')}"
            )
        else:
            lines.append(f"{index}. {op} {operation}")
    return lines or ["No operations proposed."]


def build_demo_result(canvas_path, profile_path, profile=None, selected_patch=None):
    canvas = load_canvas(canvas_path)
    profile = profile or load_profile(profile_path)
    proposal = propose_layout_patch(canvas, profile)
    patch = selected_patch or proposal["recommended_patch"]
    repaired = apply_patch_to_canvas(canvas, patch)
    audit = audit_layout(canvas, repaired)
    before_conflicts = proposal["layout_conflict_report"]
    repaired_report = propose_layout_patch(repaired, profile)["layout_conflict_report"]
    return {
        "canvas": canvas,
        "profile": profile,
        "proposal": proposal,
        "patch": patch,
        "repaired": repaired,
        "audit": audit,
        "before_conflicts": before_conflicts,
        "repaired_report": repaired_report,
        "canvas_path": canvas_path,
        "profile_path": profile_path,
    }


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_visual(path, before_canvas, after_canvas):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(render_comparison(before_canvas, after_canvas))


def print_markdown_report(result):
    proposal = result["proposal"]
    profile = result["profile"]
    audit = result["audit"]
    print("# Frame Doctor Demo Report")
    print()
    print(f"- Canvas: `{result['canvas_path']}`")
    print(f"- Profile: `{result['profile_path']}`")
    print(f"- Recommended pattern: `{result['patch']['pattern']}`")
    print(f"- Score before: {audit['before_score']}")
    print(f"- Score after: {audit['after_score']}")
    print(f"- Score delta: {audit['score_delta']}")
    print()
    print("## Layout Conflict Report")
    print()
    for line in compact_errors(result["before_conflicts"]):
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
        print(
            f"- `{candidate['pattern']}` "
            f"(confidence {candidate['confidence']:.2f}, rank {candidate.get('rank_score', 0):.2f}): "
            f"{candidate['reason']}"
        )
    print()
    print("## Human Value Profile")
    print()
    print("```json")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    print("```")
    print()
    print("## Value Decision Log")
    print()
    for item in proposal.get("value_decision_log", []):
        print(f"- `{item['step']}`: {item['message']}")
    print()
    print("## Layout Patch")
    print()
    print("```json")
    print(json.dumps(result["patch"], indent=2, ensure_ascii=False))
    print("```")
    print()
    print("## Layout QA Report")
    print()
    for line in audit.get("human_readable_summary", []):
        print(f"- {line}")
    print()
    print("Audit:")
    print("```json")
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    print("```")
    print("Remaining conflicts:")
    for line in compact_errors(result["repaired_report"]):
        print(line)


def run_demo(canvas_path, profile_path, output_json=None, visual_output=None):
    result = build_demo_result(canvas_path, profile_path)
    if output_json:
        write_json(output_json, result["repaired"])
    if visual_output:
        write_visual(visual_output, result["canvas"], result["repaired"])
    print_markdown_report(result)
    if output_json:
        print()
        print(f"Saved repaired JSON: `{output_json}`")
    if visual_output:
        print(f"Saved visual HTML: `{visual_output}`")
    return result


def _ask(prompt):
    return input(prompt).strip()


def _yes_or_default(answer):
    return answer.lower() not in ("n", "no")


def run_interactive_demo(canvas_path, profile_path):
    canvas = load_canvas(canvas_path)
    profile = load_profile(profile_path)
    proposal = propose_layout_patch(canvas, profile)

    print("# Interactive LDS Gate Mode")
    print()
    print("## Gate 1: Fact Gate")
    summary = proposal["layout_conflict_report"].get("summary", {})
    print(
        f"Conflicts: errors={summary.get('error_count', 0)}, "
        f"critical={summary.get('critical_count', 0)}, overlaps={summary.get('overlap_count', 0)}, "
        f"text_overflow={summary.get('text_overflow_count', 0)}"
    )
    if not _yes_or_default(_ask("Continue to structure hypothesis? [Y/n] ")):
        print("Stopped at Fact Gate.")
        return None

    print()
    print("## Gate 2: Meaning Gate")
    for item in proposal["semantic_role_map"]:
        print(f"- `{item['node_id']}` -> `{item['role']}` ({item['confidence']:.2f})")
    print()
    for index, candidate in enumerate(proposal["structure_candidates"], start=1):
        print(
            f"{index}. {candidate['pattern']} "
            f"(rank_score={candidate.get('rank_score', 0):.3f}) - {candidate['reason']}"
        )
    selected_patch = select_candidate_patch(proposal, _ask("Choose structure candidate number, or press Enter for recommended. "))

    print()
    print("## Gate 3: Value Gate")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    if not _yes_or_default(_ask("Use this value profile? [Y/n] ")):
        print("Available profiles:")
        for name in NAMED_VALUE_PROFILES:
            print(f"- {name}")
        selected_name = _ask("Choose profile name: ") or "readability_first"
        profile = load_named_value_profile(selected_name)
        profile_path = os.path.join(VALUE_PROFILE_DIR, NAMED_VALUE_PROFILES[selected_name])
        proposal = propose_layout_patch(canvas, profile)
        selected_patch = proposal["recommended_patch"]
        print(f"Loaded profile: {selected_name}")

    print()
    print("## Gate 4: Constraint Gate")
    print(f"Patch pattern: {selected_patch.get('pattern')}")
    for line in patch_operation_summary(selected_patch):
        print(f"- {line}")
    if not _yes_or_default(_ask("Apply this patch? [Y/n] ")):
        print("Stopped at Constraint Gate.")
        return None

    repaired = apply_patch_to_canvas(canvas, selected_patch)
    audit = audit_layout(canvas, repaired)

    print()
    print("## Gate 5: Commit Gate")
    for line in audit.get("human_readable_summary", []):
        print(f"- {line}")
    if not _yes_or_default(_ask("Accept repaired layout? [Y/n] ")):
        print("Rejected at Commit Gate.")
        return None

    result = build_demo_result(canvas_path, profile_path, profile=profile, selected_patch=selected_patch)
    print()
    print("Accepted repaired layout.")
    print_markdown_report(result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run Frame Doctor demo.")
    parser.add_argument("canvas_json", help="Path to a canvas JSON file.")
    parser.add_argument("--profile", required=True, help="Path to a value profile JSON file.")
    parser.add_argument("--output-json", help="Write the repaired canvas JSON to this path.")
    parser.add_argument("--visual-output", help="Write before/after HTML visualization to this path.")
    parser.add_argument("--interactive", action="store_true", help="Run the five LDS Gate pauses.")
    args = parser.parse_args(argv)
    if args.interactive:
        run_interactive_demo(args.canvas_json, args.profile)
    else:
        run_demo(args.canvas_json, args.profile, output_json=args.output_json, visual_output=args.visual_output)


if __name__ == "__main__":
    main()
