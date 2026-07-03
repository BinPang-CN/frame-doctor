#!/usr/bin/env python3
"""Generate an HTML before/after comparison visualization from Frame Doctor canvas JSON files."""

import argparse
import json
import os
import sys

try:
    from detect_layout_errors import detect_layout_errors, load_canvas, overlap_area, rect
except ModuleNotFoundError:
    from scripts.detect_layout_errors import detect_layout_errors, load_canvas, overlap_area, rect


# Color mapping by node role/type
ROLE_COLORS = {
    "title": ("#1a1a2e", "#e8f4fd", "#16213e"),
    "subtitle": ("#444", "#f0f4f8", "#334"),
    "body": ("#555", "#fafafa", "#444"),
    "image": ("#e3f2fd", "#bbdefb", "#1565c0"),
    "chart": ("#e8f5e9", "#c8e6c9", "#2e7d32"),
    "card": ("#fff3e0", "#ffe0b2", "#e65100"),
    "caption": ("#f3e5f5", "#e1bee7", "#7b1fa2"),
    "button": ("#fce4ec", "#f8bbd0", "#c62828"),
    "navigation": ("#e0f2f1", "#b2dfdb", "#00695c"),
    "search": ("#f5f5f5", "#e0e0e0", "#616161"),
    "tabs": ("#f5f5f5", "#e0e0e0", "#616161"),
    "kpi_card": ("#fff8e1", "#ffecb3", "#f57f17"),
    "cta": ("#fce4ec", "#f48fb1", "#880e4f"),
    "logo": ("#e8eaf6", "#c5cae9", "#283593"),
    "footer": ("#f5f5f5", "#eeeeee", "#424242"),
    "unknown": ("#eceff1", "#cfd8dc", "#546e7a"),
}

DEFAULT_COLOR = ("#eceff1", "#cfd8dc", "#37474f")


def role_color(node):
    role = node.get("role", "unknown")
    if role in ROLE_COLORS:
        return ROLE_COLORS[role]
    node_type = node.get("type", "unknown")
    if node_type in ROLE_COLORS:
        return ROLE_COLORS[node_type]
    return DEFAULT_COLOR


def role_label(node):
    role = node.get("role", node.get("type", "?"))
    node_id = node.get("id", "?")
    if len(node_id) > 12:
        node_id = node_id[:10] + "..."
    return f"{role}\n{node_id}"


def compute_overlap_regions(nodes):
    """Compute all overlap regions for visualization."""
    regions = []
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            area = overlap_area(a, b)
            if area > 0:
                ra = rect(a)
                rb = rect(b)
                ol = {
                    "x": max(ra["left"], rb["left"]),
                    "y": max(ra["top"], rb["top"]),
                    "width": max(0, min(ra["right"], rb["right"]) - max(ra["left"], rb["left"])),
                    "height": max(0, min(ra["bottom"], rb["bottom"]) - max(ra["top"], rb["top"])),
                }
                regions.append(ol)
    return regions


def _detectable_nodes(canvas):
    return [
        node for node in canvas.get("nodes", [])
        if node.get("type") != "group" and node.get("visible", True)
    ]


def generate_html(before_path, after_path, output_path, title="Frame Doctor"):
    before_canvas = load_canvas(before_path) if before_path else None
    after_canvas = load_canvas(after_path) if after_path else None

    before_name = os.path.basename(before_path) if before_path else "N/A"
    after_name = os.path.basename(after_path) if after_path else "N/A"

    # Compute metrics
    metrics = {}
    if before_canvas:
        b_errors = detect_layout_errors(before_canvas)
        b_summary = b_errors.get("summary", {})
        metrics["before_critical"] = b_summary.get("critical_count", 0)
        metrics["before_warning"] = b_summary.get("warning_count", 0)
        metrics["before_overlap"] = round(b_summary.get("total_overlap_area", 0), 1)
        metrics["before_overflow"] = round(b_summary.get("total_overflow_distance", 0), 1)

    if after_canvas:
        a_errors = detect_layout_errors(after_canvas)
        a_summary = a_errors.get("summary", {})
        metrics["after_critical"] = a_summary.get("critical_count", 0)
        metrics["after_warning"] = a_summary.get("warning_count", 0)
        metrics["after_overlap"] = round(a_summary.get("total_overlap_area", 0), 1)
        metrics["after_overflow"] = round(a_summary.get("total_overflow_distance", 0), 1)

        if before_canvas:
            try:
                from score_layout import score_layout
            except ModuleNotFoundError:
                from scripts.score_layout import score_layout
            try:
                metrics["before_score"] = score_layout(before_canvas)["score"]
            except Exception:
                metrics["before_score"] = "-"
            try:
                metrics["after_score"] = score_layout(after_canvas)["score"]
            except Exception:
                metrics["after_score"] = "-"

    # Generate HTML for one canvas
    def canvas_html(canvas_data, side_label):
        if not canvas_data:
            return f"<div class='empty-canvas'><p>No {side_label} data</p></div>"

        frame = canvas_data.get("frame", {})
        frame_w = max(float(frame.get("width", 1920)), 960)
        frame_h = max(float(frame.get("height", 1080)), 540)
        aspect = frame_w / frame_h

        # Scale to fit display area (max 720px wide per canvas)
        display_w = min(720, frame_w * 0.45)
        display_h = display_w / aspect
        if display_h > 480:
            display_h = 480
            display_w = display_h * aspect

        scale = display_w / frame_w
        nodes = _detectable_nodes(canvas_data)
        overlaps = compute_overlap_regions(nodes)

        node_rects = []
        for node in nodes:
            r = rect(node)
            bg, border, _ = role_color(node)
            label = role_label(node)
            node_rects.append(f"""<div class="node-rect" style="
                left:{r['left'] * scale}px;
                top:{r['top'] * scale}px;
                width:{max(r['width'] * scale, 1)}px;
                height:{max(r['height'] * scale, 1)}px;
                background:{bg};
                border:1.5px solid {border};
            " title="{label}">
                <span class="node-label">{label}</span>
            </div>""")

        overlap_rects = []
        for i, ol in enumerate(overlaps):
            overlap_rects.append(f"""<div class="overlap-rect" style="
                left:{ol['x'] * scale}px;
                top:{ol['y'] * scale}px;
                width:{max(ol['width'] * scale, 0)}px;
                height:{max(ol['height'] * scale, 0)}px;
            "></div>""")

        error_count = len(detect_layout_errors(canvas_data).get("errors", []))
        critical_count = sum(1 for e in detect_layout_errors(canvas_data).get("errors", []) if e.get("severity") == "critical")

        return f"""<div class="canvas-wrapper">
            <div class="canvas-label">{side_label}</div>
            <div class="canvas-stats">
                <span class="stat critical" title="Critical errors">{critical_count} critical</span>
                <span class="stat total" title="Total errors">{error_count} total</span>
                <span class="stat size">{int(frame_w)}x{int(frame_h)}</span>
            </div>
            <div class="canvas-view" style="width:{int(display_w)}px;height:{int(display_h)}px;">
                <div class="frame-outline" style="width:{int(display_w)}px;height:{int(display_h)}px;"></div>
                {''.join(node_rects)}
                {''.join(overlap_rects)}
            </div>
        </div>"""

    before_html = canvas_html(before_canvas, "BEFORE")
    after_html = canvas_html(after_canvas, "AFTER")

    # Metrics rows
    metrics_rows = ""
    if before_canvas and after_canvas:
        changes = [
            ("Critical Errors", metrics.get("before_critical", "-"), metrics.get("after_critical", "-"), "lower-better"),
            ("Warnings", metrics.get("before_warning", "-"), metrics.get("after_warning", "-"), "lower-better"),
            ("Overlap Area (px²)", metrics.get("before_overlap", "-"), metrics.get("after_overlap", "-"), "lower-better"),
            ("Overflow Distance (px)", metrics.get("before_overflow", "-"), metrics.get("after_overflow", "-"), "lower-better"),
            ("Layout Score", metrics.get("before_score", "-"), metrics.get("after_score", "-"), "higher-better"),
        ]
        for name, b_val, a_val, direction in changes:
            delta = ""
            if isinstance(b_val, (int, float)) and isinstance(a_val, (int, float)):
                d = a_val - b_val
                color = "green" if ((direction == "lower-better" and d < 0) or (direction == "higher-better" and d > 0)) else "red"
                sign = "+" if d > 0 else ""
                delta = f'<span style="color:{color}">({sign}{round(d, 1)})</span>'
            metrics_rows += f"""<tr>
                <td>{name}</td>
                <td class="before-val">{b_val}</td>
                <td class="after-val">{a_val}</td>
                <td>{delta}</td>
            </tr>"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Before/After Comparison</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: #1a1a2e;
        color: #e0e0e0;
        min-height: 100vh;
    }}
    .header {{
        padding: 32px 40px 16px;
        background: linear-gradient(135deg, #16213e, #1a1a2e);
        border-bottom: 1px solid #2a2a4a;
    }}
    .header h1 {{
        font-size: 28px;
        font-weight: 700;
        color: #64b5f6;
        margin-bottom: 4px;
    }}
    .header .subtitle {{
        font-size: 14px;
        color: #78909c;
    }}
    .main {{
        display: flex;
        gap: 24px;
        padding: 24px 40px;
        justify-content: center;
        flex-wrap: wrap;
    }}
    .canvas-wrapper {{
        background: #16213e;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }}
    .canvas-label {{
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
    .canvas-label::before {{
        content: "◉ ";
        color: #64b5f6;
    }}
    .canvas-stats {{
        display: flex;
        gap: 12px;
        margin-bottom: 12px;
    }}
    .canvas-stats .stat {{
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 12px;
        background: #1a1a2e;
    }}
    .stat.critical {{ color: #ef5350; border: 1px solid #ef5350; }}
    .stat.total {{ color: #78909c; border: 1px solid #455a64; }}
    .stat.size {{ color: #64b5f6; border: 1px solid #1e3a5f; }}
    .canvas-view {{
        position: relative;
        background: #fafbfc;
        border-radius: 6px;
        overflow: hidden;
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.08);
    }}
    .frame-outline {{
        position: absolute;
        top: 0; left: 0;
        border: 2px dashed #90a4ae;
        pointer-events: none;
        z-index: 1;
    }}
    .node-rect {{
        position: absolute;
        z-index: 2;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        cursor: default;
        overflow: hidden;
    }}
    .node-rect:hover {{
        z-index: 10;
        filter: brightness(0.92);
        box-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }}
    .node-label {{
        font-size: 9px;
        color: #333;
        text-align: center;
        line-height: 1.3;
        padding: 2px;
        white-space: pre-line;
        word-break: break-all;
    }}
    .overlap-rect {{
        position: absolute;
        z-index: 3;
        background: rgba(239, 83, 80, 0.35);
        border: 1px solid rgba(239, 83, 80, 0.7);
        pointer-events: none;
        animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 0.35; }}
        50% {{ opacity: 0.55; }}
    }}
    .metrics-section {{
        padding: 24px 40px 40px;
        max-width: 900px;
        margin: 0 auto;
    }}
    .metrics-section h2 {{
        font-size: 20px;
        margin-bottom: 16px;
        color: #64b5f6;
    }}
    .metrics-table {{
        width: 100%;
        border-collapse: collapse;
        background: #16213e;
        border-radius: 10px;
        overflow: hidden;
    }}
    .metrics-table th {{
        background: #0f3460;
        padding: 12px 16px;
        text-align: left;
        font-size: 13px;
        font-weight: 600;
        color: #90caf9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .metrics-table td {{
        padding: 10px 16px;
        font-size: 14px;
        border-bottom: 1px solid #2a2a4a;
    }}
    .metrics-table tr:last-child td {{ border-bottom: none; }}
    .before-val {{ color: #ef5350; }}
    .after-val {{ color: #66bb6a; font-weight: 600; }}
    .empty-canvas {{
        background: #16213e;
        border-radius: 12px;
        padding: 60px;
        text-align: center;
        color: #546e7a;
    }}
    @media (max-width: 1200px) {{
        .main {{ flex-direction: column; align-items: center; }}
    }}
</style>
</head>
<body>
<div class="header">
    <h1>Frame Doctor &mdash; Layout Repair Comparison</h1>
    <div class="subtitle">Before: {before_name} &nbsp;|&nbsp; After: {after_name}</div>
</div>
<div class="main">
    {before_html}
    {after_html}
</div>
<div class="metrics-section">
    <h2>Repair Metrics</h2>
    <table class="metrics-table">
        <thead>
            <tr>
                <th>Metric</th>
                <th>Before</th>
                <th>After</th>
                <th>Change</th>
            </tr>
        </thead>
        <tbody>
            {metrics_rows}
        </tbody>
    </table>
</div>
<div style="text-align:center;padding:16px;color:#455a64;font-size:12px;">
    Frame Doctor &mdash; Layout Repair Skill &mdash; LDS L0&rarr;L4 Pipeline
</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Frame Doctor before/after visualization.")
    parser.add_argument("before_json", help="Path to before canvas JSON.")
    parser.add_argument("after_json", help="Path to repaired canvas JSON (or 'none' to skip).")
    parser.add_argument("--output", default="comparison.html", help="Output HTML path.")
    parser.add_argument("--title", default="Frame Doctor", help="Report title.")
    args = parser.parse_args(argv)

    after_path = args.after_json if args.after_json.lower() != "none" else None
    output = generate_html(args.before_json, after_path, args.output, args.title)
    print(f"Visualization saved to: {output}")


if __name__ == "__main__":
    main()
