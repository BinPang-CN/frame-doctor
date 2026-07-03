# Case 01 - Shopping Dual-Task Pipeline Repair

## Files

- before: `before.png`
- after: `after.png`

## Page Type

Information mechanism explanation slide / process explanation slide.

This page explains the full mechanism from shopping list to dual-task training. It includes shopping demand input, first-person camera capture, multimodal visual recognition, structured product understanding, Goal State / risk / target / progress graph, main cognitive task, secondary cognitive task, bottom training output, and a final takeaway bar.

This is not a single card layout. Treat it as a complex system pipeline.

## Intended Reading Path

1. Enter from the top-left title.
2. Read the main flow left to right: shopping demand, camera capture, visual recognition, structured product understanding, Goal State mechanism, main/sub cognitive tasks.
3. Read the bottom training output.
4. End with the dark takeaway bar.

## Before Problems

- Critical overlap: the Goal State graph overlaps with the main cognitive task card.
- Connector clutter: blue lines pass through graph nodes, text, and cards.
- Spacing violation: process cards and product cards have inconsistent spacing.
- Hierarchy ambiguity: product cards, Goal State graph, and task cards compete for visual dominance.
- Semantic grouping failure: main/sub task panels should form a right-side task system; training output should form an independent bottom result group.
- Local stacking: text, buttons, and icons inside the recognition module collide or visually pile up.

## After Repair Intent

- Preserve all core information.
- Strengthen the left-to-right main pipeline.
- Reduce the Goal State graph and use it as a mechanism node instead of a dominant central object.
- Move main/sub cognitive tasks into a stable right sidebar.
- Organize training output as a bottom horizontal module group.
- Reduce connector complexity and route lines around text and cards.
- Normalize card size, icon position, radius, and internal padding.

## Recommended Pattern

Use `process_pipeline`.

Suggested regions:

- `header`: title and subtitle.
- `main_pipeline`: left-to-right process cards.
- `mechanism_graph`: compact Goal State node cluster.
- `task_sidebar`: main/sub cognitive task panels.
- `training_output`: bottom result modules.
- `takeaway`: final summary bar.

## Value Profile

```json
{
  "readability": 0.9,
  "visual_impact": 0.55,
  "content_preservation": 0.95,
  "grid_strictness": 0.8,
  "editability": 0.85,
  "only_fix_hard_errors": 0.0
}
```

## Repair Heuristics

- Protect the title/subtitle area before repairing the body.
- Place sequential cards on a stable horizontal grid.
- Shrink mechanism graphs when they interfere with task panels.
- Use `define_region` for pipeline, graph, sidebar, output, and takeaway areas.
- Use `route_connectors` so arrows and curves do not pass through card bodies or labels.
- Use `group` or Auto Layout metadata for repeated chips and task checklist items.
