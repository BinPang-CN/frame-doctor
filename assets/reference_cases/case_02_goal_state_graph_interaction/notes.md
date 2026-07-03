# Case 02 - Dual Goal State Graph Interaction Repair

## Files

- before: `before.png`
- after: `after.png`

## Page Type

Complex system relationship diagram / graph interaction explanation slide.

This page explains the interaction between a dual Goal State Graph and a patient's shopping process.

Core information:

1. Upper Global Shopping Goal State Graph.
2. Middle patient shopping process steps.
3. Lower Item Goal State Graph.
4. Right-side collaborative training results.
5. Bottom legend.

This is a stacked layer system: top graph, middle flow, bottom graph, right result panel, and legend.

## Intended Reading Path

1. Read title and subtitle.
2. Inspect the upper Global Shopping Goal State Graph.
3. Read the 01-06 shopping process cards from left to right.
4. Inspect the lower Item Goal State Graph.
5. Read the right-side collaborative training result panel.
6. Use the bottom legend to understand color and line semantics.

## Before Problems

- Critical title wrapping: the final title character wraps to a new line and damages the title entry area.
- Diagram overlap: graph circles collide with region labels, boundaries, and nearby content.
- Connector clutter: green, blue, gray dashed lines, and arrows cross through process cards.
- Hierarchy ambiguity: top graph, bottom graph, process cards, and result panel all compete as visual center.
- Region boundary failure: upper graph, middle process, lower graph, sidebar, and legend do not read as separate system layers.
- Legend separation weakness: the legend exists but does not clarify the dense connector semantics.

## After Repair Intent

Rebuild the slide as a stable three-layer system:

- Top Layer: Global Shopping Goal State Graph in an independent light-green container.
- Middle Layer: patient shopping process 01-06 in equal-size cards with even horizontal spacing.
- Bottom Layer: Item Goal State Graph in an independent light-blue container.
- Right Sidebar: collaborative training results, visually independent from the main system.
- Bottom Legend: unified explanation of colors, dashed lines, and loop arrows.

## Recommended Pattern

Use `layered_system_graph`.

Suggested regions:

- `header`: title and subtitle, with protected height.
- `top_global_graph`: upper system layer.
- `middle_process_flow`: six numbered process cards.
- `bottom_item_graph`: lower system layer.
- `right_results_sidebar`: collaborative training result panel.
- `bottom_legend`: line and color semantics.

## Value Profile

```json
{
  "readability": 0.95,
  "visual_impact": 0.45,
  "content_preservation": 0.95,
  "grid_strictness": 0.9,
  "editability": 0.85,
  "only_fix_hard_errors": 0.0
}
```

## Repair Heuristics

- Fix title wrapping or collision before any body repair.
- Define top/middle/bottom/right/legend regions before moving individual nodes.
- Normalize the process cards into a single horizontal row.
- Keep connector colors semantically consistent: green for upper graph update, blue for lower graph update, gray dashed for event trigger, loop arrow for dual graph collaboration.
- Route connectors outside process card bodies whenever possible.
- Preserve all graph meanings; do not simplify by deleting graph nodes or legend items.
