#!/usr/bin/env python3
"""Propose a rule-based Frame Doctor layout patch."""

import argparse
import json
import sys

try:
    from detect_layout_errors import detect_layout_errors, load_canvas
except ModuleNotFoundError:
    from scripts.detect_layout_errors import detect_layout_errors, load_canvas


DEFAULT_PROFILE = {
    "readability": 0.8,
    "visual_impact": 0.5,
    "content_preservation": 0.8,
    "grid_strictness": 0.6,
    "editability": 0.7,
    "only_fix_hard_errors": 0.0,
}


def load_profile(path):
    if not path:
        return dict(DEFAULT_PROFILE)
    with open(path, "r", encoding="utf-8") as handle:
        profile = json.load(handle)
    merged = dict(DEFAULT_PROFILE)
    merged.update(profile)
    return merged


def nodes_by_role(canvas):
    roles = {}
    for node in canvas.get("nodes", []):
        role = node.get("role", "unknown")
        roles.setdefault(role, []).append(node)
    return roles


def first_node(canvas, *roles):
    roles_map = nodes_by_role(canvas)
    for role in roles:
        if roles_map.get(role):
            return roles_map[role][0]
    return None


def semantic_role_map(canvas):
    result = []
    for node in canvas.get("nodes", []):
        role = node.get("role") or "unknown"
        confidence = 0.9 if node.get("role") else 0.35
        evidence = ["explicit role field"] if node.get("role") else ["missing role"]
        if node.get("type") == "text":
            evidence.append("text node")
        result.append(
            {
                "node_id": node.get("id"),
                "role": role,
                "confidence": confidence,
                "evidence": evidence,
            }
        )
    return result


def candidate_patterns(canvas):
    frame = canvas.get("frame", {})
    roles = nodes_by_role(canvas)
    width = frame.get("width", 0)
    height = frame.get("height", 0)
    cards = roles.get("card", [])
    has_mobile_shape = width <= 600 and height >= width

    candidates = []
    if roles.get("app_shell") or roles.get("right_sidebar") or roles.get("activity_feed") or roles.get("kpi_card"):
        candidates.append(
            {
                "pattern": "operational_dashboard",
                "confidence": 0.88,
                "reason": "App shell, KPI, chart, sidebar, or activity roles suggest an operational dashboard.",
            }
        )
    mobile_signals = [
        (
            "mobile_auth_form",
            ("form_group", "form_field", "social_login", "bottom_sheet"),
            "Form, social login, or bottom-sheet roles suggest a mobile auth/form screen.",
        ),
        (
            "mobile_profile_grid",
            ("profile_header", "avatar", "stats_row", "gallery_grid", "profile_action"),
            "Profile identity, stats, or gallery roles suggest a mobile profile/grid screen.",
        ),
        (
            "mobile_media_player",
            ("media_artwork", "media_metadata", "progress_line", "media_controls", "lyrics"),
            "Artwork, progress, or playback roles suggest a mobile media player screen.",
        ),
        (
            "mobile_ecommerce_flow",
            ("product_card", "cart_item", "checkout_summary", "filter_sheet", "variant_selector"),
            "Product, cart, checkout, or filter roles suggest a mobile e-commerce flow.",
        ),
        (
            "mobile_booking_flow",
            ("booking_field_pair", "result_card", "itinerary_summary", "booking_form"),
            "Booking fields, result cards, or itinerary roles suggest a mobile booking flow.",
        ),
        (
            "mobile_health_dashboard",
            ("health_metric_card", "service_grid", "doctor_row", "appointment_row", "mobile_chart", "nutrition_row"),
            "Health metrics, services, appointments, or nutrition roles suggest a mobile health/data screen.",
        ),
        (
            "mobile_social_messaging",
            ("chat_row", "message_bubble", "message_input", "comment_row", "video_tile", "call_controls"),
            "Chat, comment, input, or call roles suggest a mobile social/messaging screen.",
        ),
        (
            "mobile_feed_news",
            ("article_card", "featured_story", "category_control", "carousel", "author_row", "related_list"),
            "Article, carousel, author, or category roles suggest a mobile feed/news screen.",
        ),
        (
            "mobile_settings_account",
            ("settings_group", "settings_row", "divider", "toggle", "modal_panel", "destructive_action"),
            "Settings rows, toggles, dividers, or modal roles suggest a mobile settings/account screen.",
        ),
    ]
    for pattern, signal_roles, reason in mobile_signals:
        if any(roles.get(role) for role in signal_roles):
            candidates.append(
                {
                    "pattern": pattern,
                    "confidence": 0.9 if has_mobile_shape else 0.72,
                    "reason": reason,
                }
            )
    if has_mobile_shape or roles.get("navigation"):
        candidates.append(
            {
                "pattern": "mobile_screen",
                "confidence": 0.86 if has_mobile_shape else 0.68,
                "reason": "Frame shape or navigation nodes suggest a mobile stack.",
            }
        )
    if roles.get("chart") or roles.get("primary_chart") or roles.get("secondary_chart") or len(cards) >= 3:
        candidates.append(
            {
                "pattern": "dashboard",
                "confidence": 0.82 if roles.get("chart") or roles.get("primary_chart") else 0.66,
                "reason": "Chart or KPI cards suggest a dashboard layout.",
            }
        )
    if len(cards) >= 4:
        candidates.append(
            {
                "pattern": "card_grid",
                "confidence": 0.78,
                "reason": "Four or more repeated cards suggest a normalized grid.",
            }
        )
    if roles.get("title") and roles.get("body") and roles.get("image"):
        candidates.append(
            {
                "pattern": "two_column",
                "confidence": 0.84,
                "reason": "Title, body, and image can be separated into reading and media columns.",
            }
        )
    if 2 <= len(cards) <= 3:
        candidates.append(
            {
                "pattern": "comparison",
                "confidence": 0.6,
                "reason": "A small set of cards may represent comparable options.",
            }
        )

    candidates.append(
        {
            "pattern": "hero_plus_support",
            "confidence": 0.5,
            "reason": "Fallback candidate for preserving a dominant lead element with support content.",
        }
    )

    seen = set()
    unique = []
    for candidate in candidates:
        if candidate["pattern"] not in seen:
            unique.append(candidate)
            seen.add(candidate["pattern"])
    return sorted(unique, key=lambda item: item["confidence"], reverse=True)


def _move(node, x, y, width, height):
    return {
        "op": "move_resize",
        "node_id": node["id"],
        "x": round(x),
        "y": round(y),
        "width": round(width),
        "height": round(height),
    }


def _group(group_id, nodes, role):
    return {
        "op": "group",
        "group_id": group_id,
        "node_ids": [node["id"] for node in nodes if node],
        "metadata": {"role": role},
    }


def build_two_column_patch(canvas):
    frame = canvas["frame"]
    width = frame["width"]
    height = frame["height"]
    margin = max(48, min(96, int(width * 0.05)))
    gap = 48
    title = first_node(canvas, "title")
    subtitle = first_node(canvas, "subtitle")
    body = first_node(canvas, "body")
    image = first_node(canvas, "image")
    caption = first_node(canvas, "caption")
    y = margin
    operations = []

    if title:
        operations.append(_move(title, margin, y, width - margin * 2, 82))
        y += 112
    if subtitle:
        operations.append(_move(subtitle, margin, y, width - margin * 2, 48))
        y += 72

    column_width = (width - margin * 2 - gap) / 2
    content_height = height - y - margin
    caption_height = 44 if caption else 0
    caption_gap = 24 if caption else 0
    image_height = max(180, content_height - caption_height - caption_gap)

    if body:
        operations.append(_move(body, margin, y, column_width, content_height))
    if image:
        operations.append(_move(image, margin + column_width + gap, y, column_width, image_height))
    if caption:
        operations.append(
            _move(caption, margin + column_width + gap, y + image_height + caption_gap, column_width, caption_height)
        )
        operations.append(_group("group_figure", [image, caption], "figure"))

    return {
        "version": "1.0",
        "patch_id": "patch_two_column_001",
        "pattern": "two_column",
        "rationale": "Separate reading content and media into two columns to remove overlap and clarify scan order.",
        "operations": operations,
    }


def build_dashboard_patch(canvas):
    frame = canvas["frame"]
    width = frame["width"]
    height = frame["height"]
    margin = 48
    gap = 32
    roles = nodes_by_role(canvas)
    title = first_node(canvas, "title")
    nav = first_node(canvas, "navigation")
    chart = first_node(canvas, "chart")
    cards = roles.get("card", [])
    operations = []

    if title:
        operations.append(_move(title, margin, 40, width * 0.55, 64))
    if nav:
        operations.append(_move(nav, width - margin - 360, 48, 360, 48))

    kpi_y = 144
    card_height = 140
    count = max(len(cards), 1)
    card_width = (width - margin * 2 - gap * (count - 1)) / count
    for index, card in enumerate(cards):
        operations.append(_move(card, margin + index * (card_width + gap), kpi_y, card_width, card_height))

    if chart:
        chart_y = kpi_y + card_height + 48
        operations.append(_move(chart, margin, chart_y, width - margin * 2, height - chart_y - margin))

    if cards:
        operations.append(_group("group_kpi_cards", cards, "kpi_row"))
        operations.append(
            {
                "op": "apply_auto_layout",
                "target_id": "group_kpi_cards",
                "direction": "horizontal",
                "spacing": gap,
                "padding": 0,
            }
        )
    return {
        "version": "1.0",
        "patch_id": "patch_dashboard_001",
        "pattern": "dashboard",
        "rationale": "Normalize KPI cards above the chart and reserve a clear chart region.",
        "operations": operations,
    }


def build_card_grid_patch(canvas):
    frame = canvas["frame"]
    width = frame["width"]
    roles = nodes_by_role(canvas)
    cards = roles.get("card", [])
    margin = 72
    gap = 32
    columns = 2 if len(cards) <= 4 else 3
    card_width = (width - margin * 2 - gap * (columns - 1)) / columns
    card_height = 180
    operations = []
    for index, card in enumerate(cards):
        col = index % columns
        row = index // columns
        operations.append(_move(card, margin + col * (card_width + gap), 220 + row * (card_height + gap), card_width, card_height))
    if cards:
        operations.append(_group("group_card_grid", cards, "card_grid"))
    return {
        "version": "1.0",
        "patch_id": "patch_card_grid_001",
        "pattern": "card_grid",
        "rationale": "Normalize repeated cards into a grid with consistent spacing and size.",
        "operations": operations,
    }


def build_mobile_patch(canvas, pattern="mobile_screen"):
    frame = canvas["frame"]
    width = frame["width"]
    height = frame["height"]
    roles = nodes_by_role(canvas)
    operations = []
    margin = 20
    y = 24
    header = first_node(canvas, "title")
    search = first_node(canvas, "search")
    tabs = first_node(canvas, "tabs")
    navs = roles.get("navigation", [])
    cards = roles.get("card", [])

    if header:
        operations.append(_move(header, margin, y, width - margin * 2, 40))
        y += 64
    if search:
        operations.append(_move(search, margin, y, width - margin * 2, 44))
        y += 68
    if tabs:
        operations.append(_move(tabs, margin, y, width - margin * 2, 44))
        y += 68

    bottom_nav = None
    for nav in navs:
        if "bottom" in nav.get("id", ""):
            bottom_nav = nav
            break
    if not bottom_nav and navs:
        bottom_nav = navs[-1]

    available_bottom = height - 96 if bottom_nav else height - margin
    card_gap = 24
    card_height = min(150, max(96, (available_bottom - y - card_gap * max(len(cards) - 1, 0)) / max(len(cards), 1)))
    for index, card in enumerate(cards):
        operations.append(_move(card, margin, y + index * (card_height + card_gap), width - margin * 2, card_height))

    if bottom_nav:
        operations.append(_move(bottom_nav, 0, height - 76, width, 76))
        operations.append(
            {
                "op": "set_constraints",
                "node_id": bottom_nav["id"],
                "horizontal": "stretch",
                "vertical": "bottom",
            }
        )
    if cards:
        operations.append(_group("group_mobile_cards", cards, "mobile_card_stack"))
    return {
        "version": "1.0",
        "patch_id": "patch_mobile_screen_001",
        "pattern": pattern,
        "rationale": "Stack mobile content vertically and pin bottom navigation inside the frame.",
        "operations": operations,
    }


def build_fallback_patch(canvas, pattern):
    if pattern in ("dashboard", "operational_dashboard"):
        return build_dashboard_patch(canvas)
    if pattern == "card_grid":
        return build_card_grid_patch(canvas)
    if pattern == "mobile_screen" or pattern.startswith("mobile_"):
        return build_mobile_patch(canvas, pattern)
    return build_two_column_patch(canvas)


def propose_layout_patch(canvas, profile=None):
    profile = profile or dict(DEFAULT_PROFILE)
    conflicts = detect_layout_errors(canvas)
    candidates = candidate_patterns(canvas)
    recommended_pattern = candidates[0]["pattern"]
    recommended = build_fallback_patch(canvas, recommended_pattern)
    alternatives = []
    for candidate in candidates[1:3]:
        alternatives.append(build_fallback_patch(canvas, candidate["pattern"]))

    return {
        "layout_conflict_report": conflicts,
        "semantic_role_map": semantic_role_map(canvas),
        "structure_candidates": candidates[:3],
        "human_value_profile": profile,
        "recommended_patch": recommended,
        "alternatives": alternatives,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Propose a Frame Doctor layout patch.")
    parser.add_argument("canvas_json", help="Path to a canvas JSON file.")
    parser.add_argument("--profile", help="Path to a value profile JSON file.")
    args = parser.parse_args(argv)

    canvas = load_canvas(args.canvas_json)
    profile = load_profile(args.profile)
    json.dump(propose_layout_patch(canvas, profile), sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
