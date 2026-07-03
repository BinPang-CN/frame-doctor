#!/usr/bin/env python3
"""Stable Codex/LearnBuddy invocation layer for Frame Doctor."""

import argparse
import json
import os
import sys

try:
    from apply_patch_to_json import apply_patch_to_canvas
    from audit_layout import audit_layout
    from detect_layout_errors import detect_layout_errors, load_canvas
    from propose_layout_patch import propose_layout_patch
    from render_canvas_html import render_comparison
    from score_layout import score_layout
    from value_function import choose_grid_strategy, normalize_profile
except ModuleNotFoundError:
    from scripts.apply_patch_to_json import apply_patch_to_canvas
    from scripts.audit_layout import audit_layout
    from scripts.detect_layout_errors import detect_layout_errors, load_canvas
    from scripts.propose_layout_patch import propose_layout_patch
    from scripts.render_canvas_html import render_comparison
    from scripts.score_layout import score_layout
    from scripts.value_function import choose_grid_strategy, normalize_profile


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALUE_PROFILE_DIR = os.path.join(REPO_ROOT, "assets", "value_profiles")
PROFILE_SUFFIX = ".json"

TARGET_DEFAULTS = {
    "ppt": {"safe_margin": 96, "min_gutter": 32},
    "figma": {"safe_margin": 48, "min_gutter": 24},
    "dashboard": {"safe_margin": 48, "min_gutter": 32},
    "mobile": {"safe_margin": 20, "min_gutter": 16},
    "infographic": {"safe_margin": 72, "min_gutter": 32},
}


def dump_json(data, exit_code=0):
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return exit_code


def profile_path_from_arg(profile_arg):
    if not profile_arg:
        return os.path.join(VALUE_PROFILE_DIR, "readability_first.json")
    if os.path.isfile(profile_arg):
        return profile_arg
    candidate = profile_arg
    if not candidate.endswith(PROFILE_SUFFIX):
        candidate += PROFILE_SUFFIX
    path = os.path.join(VALUE_PROFILE_DIR, candidate)
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f"Unknown value profile: {profile_arg}")


def load_value_profile(profile_arg):
    path = profile_path_from_arg(profile_arg)
    with open(path, "r", encoding="utf-8") as handle:
        return normalize_profile(json.load(handle)), path


def command_diagnose(args):
    canvas = load_canvas(args.canvas_json)
    return dump_json(
        {
            "layout_conflict_report": detect_layout_errors(canvas),
            "score": score_layout(canvas),
        }
    )


def command_propose(args):
    canvas = load_canvas(args.canvas_json)
    profile, _profile_path = load_value_profile(args.profile)
    return dump_json(propose_layout_patch(canvas, profile))


def command_repair(args):
    canvas = load_canvas(args.canvas_json)
    profile, _profile_path = load_value_profile(args.profile)
    proposal = propose_layout_patch(canvas, profile)
    patch = proposal["recommended_patch"]
    repaired = apply_patch_to_canvas(canvas, patch)
    audit = audit_layout(canvas, repaired)
    repaired_report = detect_layout_errors(repaired)

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(repaired, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    if args.visual_output:
        with open(args.visual_output, "w", encoding="utf-8") as handle:
            handle.write(render_comparison(canvas, repaired))

    return dump_json(
        {
            "output": args.output,
            "visual_output": args.visual_output,
            "pattern": patch.get("pattern"),
            "before_score": audit.get("before_score"),
            "after_score": audit.get("after_score"),
            "critical_before": audit.get("conflict_reduction", {}).get("before_critical_count"),
            "critical_after": audit.get("conflict_reduction", {}).get("after_critical_count"),
            "remaining_conflicts": repaired_report.get("errors", []),
        }
    )


def command_guard(args):
    canvas = load_canvas(args.canvas_json)
    profile, profile_path = load_value_profile(args.profile)
    report = detect_layout_errors(canvas)
    score = score_layout(canvas)
    critical_count = report.get("summary", {}).get("critical_count", 0)
    payload = {
        "canvas": args.canvas_json,
        "profile": profile_path,
        "profile_values": profile,
        "layout_conflict_report": report,
        "score": score,
        "critical_count": critical_count,
        "ok": critical_count == 0,
    }
    exit_code = 1 if args.fail_on_critical and critical_count > 0 else 0
    return dump_json(payload, exit_code=exit_code)


def generation_constraints(target, profile_arg):
    profile, profile_path = load_value_profile(profile_arg)
    defaults = TARGET_DEFAULTS[target]
    pseudo_canvas = {"frame": {"width": 390 if target == "mobile" else 1920, "height": 844 if target == "mobile" else 1080}}
    grid = choose_grid_strategy(profile, pseudo_canvas)
    return {
        "target": target,
        "profile": profile_arg or "readability_first",
        "profile_path": profile_path,
        "layout_generation_constraints": {
            "safe_margin": defaults["safe_margin"],
            "min_gutter": defaults["min_gutter"],
            "preferred_grid": grid,
            "must_preserve": [
                "text",
                "images",
                "brand_style",
                "semantic_relationships",
                "editability",
            ],
            "forbidden": [
                "overlap",
                "out_of_bounds",
                "text_overflow",
                "delete_content",
                "rewrite_text",
                "replace_image",
                "change_brand_style",
                "flatten_editable_layers",
            ],
            "audit_required": True,
        },
        "recommended_generation_flow": [
            "create semantic roles",
            "choose structure hypothesis",
            "generate geometry",
            "run Frame Doctor guard",
            "repair if necessary",
            "audit before final output",
        ],
    }


def command_generation_brief(args):
    return dump_json(generation_constraints(args.target, args.profile))


def build_parser():
    parser = argparse.ArgumentParser(description="Stable Frame Doctor Skill CLI for agents.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    diagnose = subparsers.add_parser("diagnose", help="Detect conflicts and score a canvas.")
    diagnose.add_argument("canvas_json")
    diagnose.set_defaults(func=command_diagnose)

    propose = subparsers.add_parser("propose", help="Propose a value-aware repair patch.")
    propose.add_argument("canvas_json")
    propose.add_argument("--profile", default="readability_first")
    propose.set_defaults(func=command_propose)

    repair = subparsers.add_parser("repair", help="Apply the recommended patch and audit the result.")
    repair.add_argument("canvas_json")
    repair.add_argument("--profile", default="readability_first")
    repair.add_argument("--output", required=True)
    repair.add_argument("--visual-output")
    repair.set_defaults(func=command_repair)

    guard = subparsers.add_parser("guard", help="Machine-readable final geometry check.")
    guard.add_argument("canvas_json")
    guard.add_argument("--profile", default="readability_first")
    guard.add_argument("--fail-on-critical", action="store_true")
    guard.set_defaults(func=command_guard)

    brief = subparsers.add_parser("generation-brief", help="Emit generation-time layout constraints.")
    brief.add_argument("--target", required=True, choices=sorted(TARGET_DEFAULTS))
    brief.add_argument("--profile", default="readability_first")
    brief.set_defaults(func=command_generation_brief)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        return dump_json({"error": str(exc), "command": args.command}, exit_code=2)


if __name__ == "__main__":
    sys.exit(main())
