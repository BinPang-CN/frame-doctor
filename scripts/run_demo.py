#!/usr/bin/env python3
"""Run the full Frame Doctor JSON MVP loop - batch or interactive Gate-driven repair."""

import argparse
import json
import os
import sys

try:
    from apply_patch_to_json import apply_patch_to_canvas
    from audit_layout import audit_layout
    from detect_layout_errors import detect_layout_errors, load_canvas
    from propose_layout_patch import candidate_patterns, load_profile, propose_layout_patch
    from render_canvas_html import render_comparison
    from value_function import build_value_tradeoffs, normalize_profile
except ModuleNotFoundError:
    from scripts.apply_patch_to_json import apply_patch_to_canvas
    from scripts.audit_layout import audit_layout
    from scripts.detect_layout_errors import detect_layout_errors, load_canvas
    from scripts.propose_layout_patch import candidate_patterns, load_profile, propose_layout_patch
    from scripts.render_canvas_html import render_comparison
    from scripts.value_function import build_value_tradeoffs, normalize_profile


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
    patch = result["patch"]
    print("# Frame Doctor Demo Report")
    print()
    print(f"- Canvas: `{result['canvas_path']}`")
    print(f"- Profile: `{result['profile_path']}`")
    print(f"- Recommended pattern: `{patch['pattern']}`")
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
    for item in proposal.get("semantic_role_map", []):
        print(f"- `{item['node_id']}` -> `{item['role']}` ({item['confidence']:.2f})")
    print()
    print("## Structure Candidates")
    print()
    for candidate in proposal.get("structure_candidates", []):
        print(
            f"- `{candidate['pattern']}` "
            f"(confidence {candidate.get('confidence', 0):.2f}, rank {candidate.get('rank_score', 0):.2f}): "
            f"{candidate.get('reason', 'N/A')}"
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
    if patch.get("pattern"):
        tradeoffs = build_value_tradeoffs(profile, patch["pattern"])
        optimized = ", ".join(tradeoffs["optimized_for"])
        costs = ", ".join(tradeoffs["accepted_costs"])
        print(f"- `value_tradeoffs`: optimized for [{optimized}], costs: [{costs}]")
    print()
    print("## Layout Patch")
    print()
    print("```json")
    print(json.dumps(patch, indent=2, ensure_ascii=False))
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


def _ask(prompt):
    return input(prompt).strip()


def _yes_or_default(answer):
    return answer.lower() not in ("n", "no")


def gate_1_fact(canvas):
    print("\n" + "=" * 60)
    print(" GATE 1 - FACT GATE: Confirm canvas and node inventory")
    print("=" * 60)
    frame = canvas.get("frame", {})
    nodes = canvas.get("nodes", [])
    print(f"\n  Frame: {frame.get('id', 'unknown')} | {frame.get('width', '?')} x {frame.get('height', '?')}")
    print(f"  Total nodes: {len(nodes)}")
    print("\n  Node inventory:")
    for node in nodes:
        nid = node.get("id", "?")
        ntype = node.get("type", "?")
        nrole = node.get("role", "?")
        nx, ny = node.get("x", "?"), node.get("y", "?")
        nw, nh = node.get("width", "?"), node.get("height", "?")
        print(f"    [{nrole}] {nid} ({ntype}) @ ({nx},{ny}) {nw}x{nh}")

    errors = detect_layout_errors(canvas)
    summary = errors.get("summary", {})
    print(
        f"\n  Pre-scan: {summary.get('critical_count', 0)} critical, "
        f"{summary.get('warning_count', 0)} warnings, {summary.get('error_count', 0)} total"
    )
    if not _yes_or_default(_ask("  Is this the correct canvas to repair? [Y/n] ")):
        print("  Aborted by user at Gate 1.")
        sys.exit(0)
    return True


def gate_2_meaning(proposal):
    print("\n" + "=" * 60)
    print(" GATE 2 - MEANING GATE: Confirm semantic roles")
    print("=" * 60)
    print("\n  Inferred roles:")
    low_conf = []
    for item in proposal.get("semantic_role_map", []):
        flag = "  LOW CONFIDENCE" if item.get("confidence", 0) < 0.6 else ""
        print(f"    {item['node_id']:20s}  {item['role']:15s}  (conf={item['confidence']:.2f}){flag}")
        if item.get("confidence", 0) < 0.6:
            low_conf.append(item)

    if low_conf:
        print(f"\n  {len(low_conf)} node(s) have low-confidence roles.")
        for item in low_conf:
            new_role = _ask(f"  Correct role for '{item['node_id']}' [{item['role']}]: ")
            if new_role:
                item["role"] = new_role
                item["confidence"] = 0.95
                item["evidence"] = ["manual correction"]

    if not _yes_or_default(_ask("  Proceed with these semantic roles? [Y/n] ")):
        print("  Aborted by user at Gate 2.")
        sys.exit(0)
    return True


def _profile_description(code):
    descriptions = {
        "A": "Information Density",
        "B": "Readability First",
        "C": "Visual Impact",
        "D": "Grid Strictness",
        "E": "Minimal Repair",
    }
    return descriptions.get(code, "Custom")


def gate_3_value(candidates, base_profile=None):
    print("\n" + "=" * 60)
    print(" GATE 3 - VALUE GATE: Choose repair priority")
    print("=" * 60)
    print("\n  This page is primarily about:")
    print("    A. Information density - keep all content, compact layout")
    print("    B. Readability - prioritize spacing, font size, white space")
    print("    C. Visual impact - hero image, bold title, eye-catching")
    print("    D. Structural order - grid alignment, semantic grouping")
    print("    E. Minimal repair - only fix overlaps, out-of-bounds, overflow")
    if base_profile:
        print("    ENTER. Use loaded profile")

    choice = _ask("  Choose [A/B/C/D/E] (default: loaded profile or B): ").upper()
    if not choice and base_profile:
        profile = base_profile
        print("\n  Selected loaded profile.")
    else:
        choice = choice or "B"
        profiles = {
            "A": {"density": 0.9, "readability": 0.7, "visual_impact": 0.4, "grid_strictness": 0.8, "editability": 0.7, "content_preservation": 0.9},
            "B": {"readability": 0.95, "visual_impact": 0.4, "density": 0.4, "grid_strictness": 0.6, "editability": 0.8, "content_preservation": 0.8},
            "C": {"visual_impact": 0.95, "readability": 0.6, "density": 0.3, "grid_strictness": 0.4, "editability": 0.5, "content_preservation": 0.6},
            "D": {"grid_strictness": 0.95, "semantic_fidelity": 0.95, "readability": 0.8, "density": 0.7, "editability": 0.9},
            "E": {"only_fix_hard_errors": 0.95, "content_preservation": 0.95},
        }
        profile = normalize_profile(profiles.get(choice, profiles["B"]))
        print(f"\n  Selected profile: {choice} - {_profile_description(choice)}")
    print(f"  Value weights: {json.dumps(profile, indent=2)}")

    if candidates:
        winner = candidates[0]["pattern"]
        tradeoffs = build_value_tradeoffs(profile, winner)
        print(f"\n  Tradeoffs for '{winner}':")
        print(f"    Optimized for: {', '.join(tradeoffs['optimized_for'])}")
        print(f"    Accepted costs: {', '.join(tradeoffs['accepted_costs'])}")

    if not _yes_or_default(_ask("  Confirm this value profile? [Y/n] ")):
        print("  Aborted by user at Gate 3.")
        sys.exit(0)
    return profile


def gate_4_constraint(proposal):
    print("\n" + "=" * 60)
    print(" GATE 4 - CONSTRAINT GATE: Review repair plan")
    print("=" * 60)
    recommended = proposal.get("recommended_patch", {})
    operations = recommended.get("operations", [])

    print(f"\n  Recommended pattern: {recommended.get('pattern', 'unknown')}")
    print(f"  Rationale: {recommended.get('rationale', 'N/A')}")
    print(f"\n  Planned operations ({len(operations)}):")
    for line in patch_operation_summary(recommended):
        print(f"  {line}")

    movables = [op.get("node_id") for op in operations if op.get("op") == "move_resize" and op.get("node_id")]
    if movables:
        pinned = _ask("\n  Node IDs to PIN (not move, comma-separated, or ENTER to skip): ")
        if pinned:
            pinned_ids = {pid.strip() for pid in pinned.split(",") if pid.strip()}
            kept = []
            for op in operations:
                if op.get("op") == "move_resize" and op.get("node_id") in pinned_ids:
                    print(f"    SKIPPED: {op.get('node_id')} (pinned)")
                    continue
                kept.append(op)
            recommended["operations"] = kept
            print(f"    Kept {len(kept)}/{len(operations)} operations.")

    alternatives = proposal.get("alternatives", [])
    if alternatives:
        print("\n  Alternative strategies available:")
        for index, alt in enumerate(alternatives, start=1):
            print(f"    {index}. {alt.get('pattern', '?')} - {alt.get('rationale', 'N/A')[:80]}")
        alt_choice = _ask("  Switch to alternative [1/2/skip]: ")
        if alt_choice == "1":
            proposal["recommended_patch"] = alternatives[0]
            print("  Switched to alternative 1.")
        elif alt_choice == "2" and len(alternatives) > 1:
            proposal["recommended_patch"] = alternatives[1]
            print("  Switched to alternative 2.")

    if not _yes_or_default(_ask("  Apply this repair plan? [Y/n] ")):
        print("  Aborted by user at Gate 4.")
        sys.exit(0)
    return proposal


def gate_5_commit(audit_report):
    print("\n" + "=" * 60)
    print(" GATE 5 - COMMIT GATE: Post-repair QA")
    print("=" * 60)
    print(f"\n  Score: {audit_report['before_score']} -> {audit_report['after_score']} (delta={audit_report['score_delta']})")
    reduction = audit_report.get("conflict_reduction", {})
    print(f"  Critical errors: {reduction.get('before_critical_count', '?')} -> {reduction.get('after_critical_count', '?')}")
    print(f"  Total errors: {reduction.get('before_error_count', '?')} -> {reduction.get('after_error_count', '?')}")

    metrics = audit_report.get("metric_deltas", {})
    print(f"  Overlap area: {metrics.get('overlap_area_before', '?')} -> {metrics.get('overlap_area_after', '?')}")
    print(f"  Overflow distance: {metrics.get('overflow_distance_before', '?')} -> {metrics.get('overflow_distance_after', '?')}")
    print(f"  Alignment drift: {metrics.get('alignment_drift_before', '?')} -> {metrics.get('alignment_drift_after', '?')}")
    print(f"  Layout stability: {metrics.get('layout_stability', '?')}")

    remaining = audit_report.get("remaining_conflicts", [])
    if remaining:
        print(f"\n  Remaining issues ({len(remaining)}):")
        for error in remaining[:5]:
            nodes = ", ".join(str(node) for node in error.get("nodes", []))
            print(f"    - {error.get('severity', '?')} {error.get('type', '?')} on {nodes}")
        if len(remaining) > 5:
            print(f"    ... and {len(remaining) - 5} more")

    if not _yes_or_default(_ask("  Accept this repair and deliver? [Y/n] ")):
        print("  Repair rejected. Canvas reverted.")
        return False
    print("  Repair accepted and delivered.")
    return True


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


def run_interactive_demo(canvas_path, profile_path=None):
    canvas = load_canvas(canvas_path)
    base_profile = load_profile(profile_path) if profile_path else None

    gate_1_fact(canvas)
    profile = gate_3_value(candidate_patterns(canvas), base_profile=base_profile)
    proposal = propose_layout_patch(canvas, profile)
    gate_2_meaning(proposal)
    proposal = gate_4_constraint(proposal)

    patch = proposal.get("recommended_patch", {})
    repaired = apply_patch_to_canvas(canvas, patch)
    audit = audit_layout(canvas, repaired)

    if not gate_5_commit(audit):
        sys.exit(1)

    result = build_demo_result(canvas_path, profile_path or "interactive", profile=profile, selected_patch=patch)
    print()
    print_markdown_report(result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run Frame Doctor demo.")
    parser.add_argument("canvas_json", help="Path to a canvas JSON file.")
    parser.add_argument("--profile", help="Path to a value profile JSON file.")
    parser.add_argument("--output-json", help="Write the repaired canvas JSON to this path.")
    parser.add_argument("--visual-output", help="Write before/after HTML visualization to this path.")
    parser.add_argument("--interactive", action="store_true", help="Run the five LDS Gate pauses.")
    args = parser.parse_args(argv)

    if args.interactive:
        run_interactive_demo(args.canvas_json, args.profile)
    else:
        profile = args.profile or os.path.join("assets", "value_profiles", "readability_first.json")
        run_demo(args.canvas_json, profile, output_json=args.output_json, visual_output=args.visual_output)


if __name__ == "__main__":
    main()
