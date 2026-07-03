# Grid Constraints

Frame Doctor may use grid constraints when the canvas already exists but its spatial order is unstable. This reference is distilled from the local LDS Grid Reference Pack and should be treated as an execution aid, not as a design-history summary.

## Core Idea

A grid is not decoration. It is a constraint system for relationships between text, images, charts, color blocks, and whitespace. Use it to make layout repair measurable and auditable.

## Terms

- `type_area`: Main content area inside safe margins.
- `margin`: Safe distance between content and frame edge.
- `column`: Vertical structure used by text, media, and grouped content.
- `gutter`: Space between columns, cards, modules, or image-caption pairs.
- `field`: Smallest module in a modular grid.
- `baseline_grid`: Rhythm used to align body, caption, and annotation text.
- `image_caption_pair`: Image/chart and its explanatory caption.
- `grid_granularity`: Number of fields; larger grids allow more density but require stricter discipline.

## Grid Families

- 2/3/4-column grid: use for readability-first slides, reports, and explanation pages.
- 8-field modular grid: use for stable, easy-to-explain repairs.
- 20-field modular grid: use for mixed text, images, cards, charts, and captions.
- 32-field modular grid: use for high-density dashboards or complex infographics when strict grid discipline is high.
- Hierarchy-first grid: allow title or hero image to span fields when visual impact is prioritized, while keeping edges aligned.

## Detection Mapping

- `margin_breach`: node violates safe margin or type area.
- `column_drift`: related nodes drift from shared column edges or centers.
- `gutter_anomaly`: repeated gaps are inconsistent or below minimum readable spacing.
- `baseline_mismatch`: text rhythm does not match declared baseline.
- `image_caption_detachment`: caption is too far from or misaligned with its image/chart.
- `snap_error`: average edge distance from the nearest declared grid line.

## Value Mapping

- Higher `readability`: prefer stable columns, readable line length, clear image-caption distance, and generous gutters.
- Higher `visual_impact`: allow larger titles, hero media, and field-spanning elements, but keep edges on grid lines.
- Higher `density`: prefer 20-field or 32-field modular grids.
- Higher `grid_strictness`: reduce snap error, normalize gutters, and align repeated modules.
- Higher `editability`: create semantic groups and Auto Layout/constraint metadata.
- Higher `semantic_fidelity`: preserve content meaning, image-caption pairing, and reading order.

## Audit Checklist

After repair, verify:

- No overlap, out-of-bounds placement, or text overflow remains.
- Declared margins and type area are respected.
- Related elements share column or field boundaries.
- Gutters are consistent for repeated components.
- Image/chart captions remain attached and aligned.
- Title, body, caption, and supporting information have clear hierarchy.
- Editable groups, constraints, or Auto Layout metadata are present where useful.
