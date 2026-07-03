#!/usr/bin/env python3
"""Render Frame Doctor canvas JSON as dependency-free HTML."""

import argparse
import html
import itertools
import json
import sys

try:
    from audit_layout import audit_layout
    from detect_layout_errors import detect_layout_errors, load_canvas, overlap_area, rect
    from score_layout import score_layout
except ModuleNotFoundError:
    from scripts.audit_layout import audit_layout
    from scripts.detect_layout_errors import detect_layout_errors, load_canvas, overlap_area, rect
    from scripts.score_layout import score_layout


ROLE_CLASSES = {
    "title": "role-title",
    "subtitle": "role-subtitle",
    "body": "role-text",
    "caption": "role-caption",
    "image": "role-image",
    "chart": "role-chart",
    "card": "role-card",
    "kpi_card": "role-card",
    "navigation": "role-chrome",
    "footer": "role-chrome",
}


def role_class(node):
    role = str(node.get("role") or "")
    node_type = str(node.get("type") or "")
    return ROLE_CLASSES.get(role) or ROLE_CLASSES.get(node_type) or "role-generic"


def frame_scale(frame, max_width=720):
    width = max(float(frame.get("width", 1)), 1.0)
    return min(1.0, float(max_width) / width)


def _style_number(value):
    return f"{float(value):.2f}px"


def _node_is_out_of_bounds(node, frame):
    r = rect(node)
    return (
        r["left"] < 0
        or r["top"] < 0
        or r["right"] > float(frame.get("width", 0))
        or r["bottom"] > float(frame.get("height", 0))
    )


def render_node(node, scale):
    node_id = html.escape(str(node.get("id", "node")))
    role = html.escape(str(node.get("role", "unknown")))
    node_type = html.escape(str(node.get("type", "unknown")))
    text = html.escape(str(node.get("text", "")))
    classes = ["node", role_class(node)]
    if node.get("_render_out_of_bounds"):
        classes.append("out-of-bounds")
    style = (
        f"left:{_style_number(float(node.get('x', 0)) * scale)};"
        f"top:{_style_number(float(node.get('y', 0)) * scale)};"
        f"width:{_style_number(float(node.get('width', 0)) * scale)};"
        f"height:{_style_number(float(node.get('height', 0)) * scale)};"
    )
    preview = f'<div class="node-text">{text}</div>' if text else ""
    return (
        f'<div class="{" ".join(classes)}" style="{style}" title="{node_id} / {role}">'
        f'<div class="node-label"><strong>{node_id}</strong><span>{role} · {node_type}</span></div>'
        f"{preview}</div>"
    )


def _render_overlap_overlays(canvas, scale):
    overlays = []
    nodes = [node for node in canvas.get("nodes", []) if node.get("type") != "group" and node.get("visible", True)]
    for a, b in itertools.combinations(nodes, 2):
        if overlap_area(a, b) <= 0:
            continue
        ra = rect(a)
        rb = rect(b)
        left = max(ra["left"], rb["left"]) * scale
        top = max(ra["top"], rb["top"]) * scale
        width = (min(ra["right"], rb["right"]) - max(ra["left"], rb["left"])) * scale
        height = (min(ra["bottom"], rb["bottom"]) - max(ra["top"], rb["top"])) * scale
        style = (
            f"left:{_style_number(left)};top:{_style_number(top)};"
            f"width:{_style_number(width)};height:{_style_number(height)};"
        )
        overlays.append(f'<div class="overlap-overlay" style="{style}"></div>')
    return "\n".join(overlays)


def render_error_list(report):
    errors = report.get("errors", [])
    if not errors:
        return '<p class="empty">No layout conflicts detected.</p>'
    items = []
    for error in errors:
        severity = html.escape(str(error.get("severity", "unknown")))
        error_type = html.escape(str(error.get("type", "unknown")))
        nodes = html.escape(", ".join(str(node) for node in error.get("nodes", [])))
        message = html.escape(str(error.get("message", "")))
        items.append(f"<li><strong>{severity}</strong> <code>{error_type}</code> on {nodes}: {message}</li>")
    return f'<ul class="error-list">{"".join(items)}</ul>'


def _metric_rows(report):
    summary = report.get("summary", {})
    keys = [
        ("error_count", "Errors"),
        ("critical_count", "Critical"),
        ("overlap_count", "Overlaps"),
        ("out_of_bounds_count", "Out of bounds"),
        ("text_overflow_count", "Text overflow"),
        ("hierarchy_ambiguity_count", "Hierarchy ambiguity"),
    ]
    rows = []
    for key, label in keys:
        rows.append(
            "<div class=\"metric\"><span>"
            + html.escape(label)
            + "</span><strong>"
            + html.escape(str(summary.get(key, 0)))
            + "</strong></div>"
        )
    return "\n".join(rows)


def render_single_canvas(canvas, title):
    report = detect_layout_errors(canvas)
    score = score_layout(canvas)
    frame = canvas.get("frame", {})
    scale = frame_scale(frame)
    frame_width = float(frame.get("width", 1)) * scale
    frame_height = float(frame.get("height", 1)) * scale
    nodes = []
    for node in canvas.get("nodes", []):
        if node.get("type") == "group" or not node.get("visible", True):
            continue
        renderable = dict(node)
        renderable["_render_out_of_bounds"] = _node_is_out_of_bounds(node, frame)
        nodes.append(render_node(renderable, scale))
    safe_title = html.escape(title)
    return f"""
<section class="canvas-section">
  <div class="section-head">
    <h2>{safe_title}</h2>
    <span class="score">Score {html.escape(str(score.get("score", 0)))}</span>
  </div>
  <div class="canvas-wrap" style="width:{_style_number(frame_width)};">
    <div class="frame" style="width:{_style_number(frame_width)};height:{_style_number(frame_height)};">
      {_render_overlap_overlays(canvas, scale)}
      {"".join(nodes)}
    </div>
  </div>
  <aside class="side-panel">
    <h3>Conflict Summary</h3>
    <div class="metrics">{_metric_rows(report)}</div>
    {render_error_list(report)}
  </aside>
</section>
"""


def _comparison_summary(before_canvas, after_canvas):
    audit = audit_layout(before_canvas, after_canvas)
    rows = [
        ("Score", audit.get("before_score"), audit.get("after_score")),
        (
            "Critical conflicts",
            audit.get("conflict_reduction", {}).get("before_critical_count"),
            audit.get("conflict_reduction", {}).get("after_critical_count"),
        ),
        (
            "Overlap area",
            audit.get("metric_deltas", {}).get("overlap_area_before"),
            audit.get("metric_deltas", {}).get("overlap_area_after"),
        ),
        (
            "Remaining conflicts",
            audit.get("conflict_reduction", {}).get("before_error_count"),
            audit.get("conflict_reduction", {}).get("after_error_count"),
        ),
    ]
    cells = []
    for label, before, after in rows:
        cells.append(
            "<tr><th>"
            + html.escape(str(label))
            + "</th><td>"
            + html.escape(str(before))
            + "</td><td>"
            + html.escape(str(after))
            + "</td></tr>"
        )
    return f"""
<section class="audit-summary">
  <h2>Metric Summary</h2>
  <table>
    <thead><tr><th>Metric</th><th>Before</th><th>After</th></tr></thead>
    <tbody>{"".join(cells)}</tbody>
  </table>
</section>
"""


def _document(body, title="Frame Doctor Visual Render"):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --ink:#0d2847; --muted:#64748b; --line:#cbd5e1; --bg:#f8fafc;
      --teal:#009f92; --blue:#2563eb; --orange:#f97316; --red:#dc2626;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; padding:32px; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:var(--ink); background:var(--bg); }}
    h1 {{ margin:0 0 24px; font-size:28px; }}
    h2 {{ margin:0; font-size:20px; }}
    h3 {{ margin:0 0 12px; font-size:15px; }}
    code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
    .comparison {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; align-items:start; }}
    .canvas-section {{ display:grid; grid-template-columns:minmax(320px, auto) 280px; gap:18px; margin-bottom:28px; align-items:start; }}
    .comparison .canvas-section {{ grid-template-columns:1fr; }}
    .section-head {{ display:flex; align-items:center; justify-content:space-between; grid-column:1 / -1; }}
    .score {{ color:var(--muted); font-weight:700; }}
    .frame {{ position:relative; overflow:visible; background:#fff; border:2px solid #94a3b8; box-shadow:0 16px 40px rgba(15,23,42,.10); }}
    .node {{ position:absolute; border:2px solid #64748b; border-radius:8px; padding:8px; overflow:hidden; background:rgba(255,255,255,.88); }}
    .node-label {{ display:flex; flex-direction:column; gap:2px; font-size:11px; line-height:1.2; }}
    .node-label span {{ color:var(--muted); }}
    .node-text {{ margin-top:8px; font-size:11px; color:#334155; line-height:1.35; }}
    .role-title {{ border-color:var(--ink); background:#eff6ff; }}
    .role-subtitle,.role-text {{ border-color:#94a3b8; background:#fff; }}
    .role-caption {{ border-style:dashed; border-color:#0f766e; background:#ecfdf5; }}
    .role-image {{ border-color:var(--blue); background:repeating-linear-gradient(135deg,#dbeafe,#dbeafe 10px,#eff6ff 10px,#eff6ff 20px); }}
    .role-chart {{ border-color:var(--orange); background:#fff7ed; }}
    .role-card {{ border-color:var(--teal); background:#ecfeff; }}
    .role-chrome {{ border-color:#475569; background:#f1f5f9; }}
    .out-of-bounds {{ outline:4px solid var(--red); outline-offset:2px; }}
    .overlap-overlay {{ position:absolute; z-index:4; background:rgba(220,38,38,.22); border:1px solid rgba(220,38,38,.55); pointer-events:none; }}
    .node {{ z-index:5; }}
    .side-panel,.audit-summary {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:16px; box-shadow:0 10px 24px rgba(15,23,42,.06); }}
    .metrics {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px; }}
    .metric {{ border:1px solid #e2e8f0; border-radius:8px; padding:8px; }}
    .metric span {{ display:block; color:var(--muted); font-size:11px; }}
    .metric strong {{ font-size:18px; }}
    .error-list {{ margin:0; padding-left:18px; color:#334155; font-size:13px; line-height:1.45; }}
    .empty {{ margin:0; color:var(--muted); }}
    table {{ width:100%; border-collapse:collapse; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:10px; text-align:left; }}
    @media (max-width: 1200px) {{
      .comparison,.canvas-section {{ grid-template-columns:1fr; }}
      body {{ padding:18px; }}
    }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  {body}
</body>
</html>
"""


def render_comparison(before_canvas, after_canvas):
    body = (
        _comparison_summary(before_canvas, after_canvas)
        + '<div class="comparison">'
        + render_single_canvas(before_canvas, "Before")
        + render_single_canvas(after_canvas, "After")
        + "</div>"
    )
    return _document(body, "Frame Doctor Before / After")


def render_html(before_canvas, after_canvas=None):
    if after_canvas is not None:
        return render_comparison(before_canvas, after_canvas)
    return _document(render_single_canvas(before_canvas, "Canvas"), "Frame Doctor Canvas")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render Frame Doctor canvas JSON as HTML.")
    parser.add_argument("canvas_json", help="Path to the before canvas JSON file.")
    parser.add_argument("--after", help="Optional repaired canvas JSON file for side-by-side compare.")
    parser.add_argument("--output", required=True, help="HTML output path.")
    args = parser.parse_args(argv)

    before_canvas = load_canvas(args.canvas_json)
    after_canvas = load_canvas(args.after) if args.after else None
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(render_html(before_canvas, after_canvas))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
