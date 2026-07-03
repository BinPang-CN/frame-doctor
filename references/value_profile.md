# Value Profile

A value profile is the human priority model for layout repair. It should be confirmed before changing layout unless the user asks for automatic mode.

## Priorities

- `readability`: Favor clear reading order, adequate text width, line length, and separation.
- `visual_impact`: Favor stronger primary visual hierarchy and bolder content presence.
- `content_preservation`: Favor minimal edits to size and placement so all original material remains intact.
- `grid_strictness`: Favor exact alignment, repeated dimensions, and consistent spacing.
- `editability`: Favor grouped, constraint-friendly, and Auto Layout-ready structures.
- `density`: Favor modular grids that can hold more information without overlap.
- `semantic_fidelity`: Favor keeping image-caption relationships, reading order, and content meaning intact.
- `only_fix_hard_errors`: Fix only objective critical conflicts such as overlap, out-of-bounds, and text overflow.

## Example Profile

```json
{
  "readability": 0.9,
  "visual_impact": 0.4,
  "content_preservation": 0.9,
  "grid_strictness": 0.7,
  "editability": 0.8,
  "only_fix_hard_errors": 0.0
}
```

## Use Guidance

Higher `readability` should increase spacing and preserve text boxes. Higher `visual_impact` may allocate more area to hero images or charts. Higher `grid_strictness` should prefer snapped edges, consistent gutters, and stable type areas. Higher `density` may justify 20-field or 32-field grids. Higher `semantic_fidelity` should keep captions attached to images and avoid changes that break meaning. Higher `editability` should prefer grouping, constraints, and Auto Layout metadata. Higher `only_fix_hard_errors` should avoid broad restacking when objective errors can be solved locally.
