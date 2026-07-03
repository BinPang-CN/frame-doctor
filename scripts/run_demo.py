#!/usr/bin/env python3
"""Run the full Frame Doctor JSON MVP loop — batch or interactive Gate-driven repair."""

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
    from value_function import build_value_tradeoffs, normalize_profile, DEFAULT_PROFILE
except ModuleNotFoundError:
    from scripts.apply_patch_to_json import apply_patch_to_canvas
    from scripts.audit_layout import audit_layout
    from scripts.detect_layout_errors import detect_layout_errors, load_canvas
    from scripts.propose_layout_patch import candidate_patterns, load_profile, propose_layout_patch
    from scripts.render_canvas_html import render_comparison
    from scripts.value_function import build_value_tradeoffs, normalize_profile, DEFAULT_PROFILE


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
        print(f"- `value_tradeoffs`: optimized for [{', '.join(tradeoffs['optimized_for'])}], costs: [{', '.join(tradeoffs['accepted_costs'])}]")
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


# ---- Interactive Gate helpers ----

def _prompt(prompt_text):
    sys.stderr.write(f"\n{prompt_text}\n> ")
    sys.stderr.flush()
    try:
        return input().strip()
    except EOFError:
        return ""


def _confirm(prompt_text, default="y"):
    ans = _prompt(f"{prompt_text} [y/N]" if default == "n" else f"{prompt_text} [Y/n]").lower()
    if not ans:
        return default == "y"
    return ans in ("y", "yes")


def _ask(prompt):
    return input(prompt).strip()


def _yes_or_default(answer):
    return answer.lower() not in ("n", "no")


# ---- Rich Gate Implementations ----

def gate_1_fact(canvas):
    """GATE 1 – Fact Gate: confirm canvas identity and node inventory."""
    print("\n" + "=" * 60)
    print(" GATE 1 — FACT GATE: Confirm canvas and node inventory")
    print("=" * 60)
    frame = canvas.get("frame", {})
    nodes = canvas.get("nodes", [])
    print(f"\n  Frame: {frame.get('id', 'unknown')}  |  {frame.get('width', '?')} x {frame.get('height', '?')}")
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
    print(f"\n  Pre-scan: {summary.get('critical_count', 0)} critical, {summary.get('warning_count', 0)} warnings, {summary.get('error_count', 0)} total")
    if not _yes_or_default(_ask("  Is this the correct canvas to repair? [Y/n] ")):
        print("  Aborted by user at Gate 1.")
        sys.exit(0)
    return True


def gate_2_meaning(proposal):
    """GATE 2 – Meaning Gate: confirm semantic role mapping."""
    print("\n" + "=" * 60)
    print(" GATE 2 — MEANING GATE: Confirm semantic roles")
    print("=" * 60)
    print("\n  Inferred roles:")
    role_map = proposal.get("semantic_role_map", [])
    low_conf = []
    for item in role_map:
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


def gate_3_value(candidates):
    """GATE 3 – Value Gate: choose repair priority with A/B/C/D/E shortcuts."""
    print("\n" + "=" * 60)
    print(" GATE 3 — VALUE GATE: Choose repair priority")
    print("=" * 60)
    print("\n  This page is primarily about:")
    print("    A. Information density — keep all content, compact layout")
    print("    B. Readability — prioritize spacing, font size, white space")
    print("    C. Visual impact — hero image, bold title, eye-catching")
    print("    D. Structural order — grid alignment, semantic grouping")
    print("    E. Minimal repair — only fix overlaps, out-of-bounds, overflow")

    choice = _ask("  Choose [A/B/C/D/E] (default: B): ").upper() or "B"

    profiles = {
        "A": {"density": 0.9, "readability": 0.7, "visual_impact": 0.4, "grid_strictness": 0.8, "editability": 0.7, "content_preservation": 0.9},
        "B": {"readability": 0.95, "visual_impact": 0.4, "density": 0.4, "grid_strictness": 0.6, "editability": 0.8, "content_preservation": 0.8},
        "C": {"visual_impact": 0.95, "readability": 0.6, "density": 0.3, "grid_strictness": 0.4, "editability": 0.5, "content_preservation": 0.6},
        "D": {"grid_strictness": 0.95, "semantic_fidelity": 0.95, "readability": 0.8, "density": 0.7, "editability": 0.9},
        "E": {"only_fix_hard_errors": 0.95, "content_preservation": 0.95},
    }
    profile = normalize_profile(profiles.get(choice, profiles["B"]))
    print(f"\n  Selected profile: {choice} — {_profile_description(choice)}")
    print(f"  Value weights: {json.dumps(profile, indent=2)}")

    if candidates:
        winner = candidates[0]["pattern"]
        tradeoffs = build_value_tradeoffs(profile, winner)
        print(f"\n   Tradeoffs for '{winner}':")
        print(f"    Optimized for: {', '.join(tradeoffs['optimized_for'])}")
        print(f"    Accepted costs: {', '.join(tradeoffs['accepted_costs'])}")

    if not _yes_or_default(_ask("  Confirm this value profile? [Y/n] ")):
        print("  Aborted by user at Gate 3.")
        sys.exit(0)
    return profile


def _profile_description(code):
    return {"A": "Information Density", "B": "Readability First", "C": "Visual Impact", "D": "Grid Strictness", "E": "Minimal Repair"}.get(code, "Custom")


def gate_4_constraint(proposal):
    """GATE 4 – Constraint Gate: review plan, pin elements, switch alternatives."""
    print("\n" + "=" * 60)
    print(" GATE 4 — CONSTRAINT GATE: Review repair plan")
    print("=" * 60)
    recommended = proposal.get("recommended_patch", {})
    pattern = recommended.get("pattern", "unknown")
    operations = recommended.get("operations", [])

    print(f"\n  Recommended pattern: {pattern}")
    print(f"  Rationale: {recommended.get('rationale', 'N/A')}")
    print(f"\n  Planned operations ({len(operations)}):")

    # Use cleaner operation summary
    for line in patch_operation_summary(recommended):
        print(f"  {line}")

    # Pin constraint
    movables = [op.get("node_id") for op in operations if op.get("op") == "move_resize" and op.get("node_id")]
    if movables:
        pinned = _ask("\n  Node IDs to PIN (not move, comma-separated, or ENTER to skip): ")
        if pinned:
            pinned_ids = set(pid.strip() for pid in pinned.split(",") if pid.strip())
            ops_kept = []
            for op in operations:
                if op.get("op") == "move_resize" and op.get("node_id") in pinned_ids:
                    print(f"    SKIPPED: {op.get('node_id')} (pinned)")
                    continue
                ops_kept.append(op)
            recommended["operations"] = ops_kept
            print(f"    Kept {len(ops_kept)}/{len(operations)} operations.")

    # Alternative strategies
    alts = proposal.get("alternatives", [])
    if alts:
        print("\n  Alternative strategies available:")
        for i, alt in enumerate(alts):
            print(f"    {i+1}. {alt.get('pattern', '?')} — {alt.get('rationale', 'N/A')[:80]}")
        alt_choice = _ask("  Switch to alternative [1/2/skip]: ")
        if alt_choice == "1" and alts:
            proposal["recommended_patch"] = alts[0]
            print("  Switched to alternative 1.")
        elif alt_choice == "2" and len(alts) > 1:
            proposal["recommended_patch"] = alts[1]
            print("  Switched to alternative 2.")

    if not _yes_or_default(_ask("  Apply this repair plan? [Y/n] ")):
        print("  Aborted by user at Gate 4.")
        sys.exit(0)
    return proposal


def gate_5_commit(before_canvas, repaired_canvas, audit_report):
    """GATE 5 – Commit Gate: review QA and confirm final delivery."""
    print("\n" + "=" * 60)
    print(" GATE 5 — COMMIT GATE: Post-repair QA")
    print("=" * 60)
    print(f"\n  Score: {audit_report['before_score']}  {audit_report['after_score']}  (D={audit_report['score_delta']})")
    cr = audit_report.get("conflict_reduction", {})
    print(f"  Critical errors: {cr.get('before_critical_count', '?')}  {cr.get('after_critical_count', '?')}")
    print(f"  Total errors: {cr.get('before_error_count', '?')}  {cr.get('after_error_count', '?')}")

    md = audit_report.get("metric_deltas", {})
    print(f"  Overlap area: {md.get('overlap_area_before', '?')}  {md.get('overlap_area_after', '?')} (D={md.get('overlap_area_reduction', '?')})")
    print(f"  Overflow distance: {md.get('overflow_distance_before', '?')}  {md.get('overflow_distance_after', '?')}  (D={md.get('overflow_distance_reduction', '?')})")
    print(f"  Alignment drift: {md.get('alignment_drift_before', '?')}  {md.get('alignment_drift_after', '?')}  (D={md.get('alignment_drift_reduction', '?')})")
    print(f"  Layout stability: {md.get('layout_stability', '?')}")

    remaining = audit_report.get("remaining_conflicts", [])
    if remaining:
        print(f"\n  Remaining issues ({len(remaining)}):")
        for err in remaining[:5]:
            nodes_str = ", ".join(str(n) for n in err.get("nodes", []))
            print(f"    - {err.get('severity', '?')} {err.get('type', '?')} on {nodes_str}")
        if len(remaining) > 5:
            print(f"    ... and {len(remaining) - 5} more")

    print("\n  Suggested manual review:")
    print("    - Does the layout match the presentation narrative?")
    print("    - Are key visuals positioned for maximum impact?")
    print("    - Is the card/sequence order logical?")
    print("    - Does the white-space balance feel right?")

    if not _yes_or_default(_ask("  Accept this repair and deliver? [Y/n] ")):
        print("  Repair rejected. Canvas reverted.")
        return False
    print("   Repair accepted and delivered!")
    return True


# ---- Main entry points ----

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
    """Five-Gate interactive LDS repair flow."""
    canvas = load_canvas(canvas_path)

    gate_1_fact(canvas)

    # Pre-detect for candidates
    candidates = candidate_patterns(canvas)
    profile = gate_3_value(candidates)

    # Run proposal with chosen value profile
    proposal = propose_layout_patch(canvas, profile)
    gate_2_meaning(proposal)
    proposal = gate_4_constraint(proposal)

    patch = proposal.get("recommended_patch", {})
    repaired = apply_patch_to_canvas(canvas, patch)
    audit = audit_layout(canvas, repaired)

    if not gate_5_commit(canvas, repaired, audit):
        sys.exit(1)

    # Build and print final result
    result = build_demo_result(canvas_path, profile_path or "interactive", profile=profile, selected_patch=patch)
    print()
    print_markdown_report(result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run Frame Doctor demo.")
    parser.add_argument("canvas_json", help="Path to a canvas JSON file.")
    parser.add_argument("--profile", help="Path to a value profile JSON file (optional in interactive mode).")
    parser.add_argument("--output-json", help="Write the repaired canvas JSON to this path.")
    parser.add_argument("--visual-output", help="Write before/after HTML visualization to this path.")
    parser.add_argument("--interactive", action="store_true", help="Run the five LDS Gate pauses.")
    args = parser.parse_args(argv)

    if args.interactive:
        run_interactive_demo(args.canvas_json, args.profile)
    else:
        if not args.profile:
            args.profile = os.path.join("assets", "value_profiles", "readability_first.json")
        run_demo(args.canvas_json, args.profile, output_json=args.output_json, visual_output=args.visual_output)


if __name__ == "__main__":
    main()
