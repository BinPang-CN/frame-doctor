# Case 03 - Dashboard Data Page Reference

## Source

- Figma file: `https://www.figma.com/design/bwMC88Ow4ZBflUZsHaWDGm/Figma%E6%A0%BC%E5%BC%8F?node-id=0-1`
- Reference frame: `01_Light_GenericDashboard`
- Local reference image: `figma_reference.png`

## Page Type

Operational dashboard / admin analytics page.

This reference contains a persistent left navigation, top title/search/notification bar, top KPI summary cards, primary line chart, secondary bar and pie charts, right sidebar with server status, recent problems, and latest activity, plus lower review cards.

## Intended Reading Path

1. Left app shell establishes product context but should not dominate.
2. Top bar gives page title and global actions.
3. KPI row gives the fastest summary.
4. Primary line chart carries the main analytic story.
5. Secondary bar/pie modules provide supporting breakdowns.
6. Right sidebar gives operational status and activity feed.
7. Lower review cards or records are tertiary content.

## Transferable Layout Pattern

Use the `dashboard` pattern with explicit regions:

- `app_shell`: fixed-width left navigation.
- `top_bar`: title, subtitle, notification, profile, and search.
- `kpi_row`: three equal summary cards.
- `primary_chart`: full-width line chart inside main content lane.
- `secondary_analytics`: two equal chart cards.
- `right_sidebar`: status chart, problem list, activity timeline.
- `record_area`: lower review cards or data records.

## Useful Repair Lessons

- The main content lane and right sidebar must remain visually separate.
- KPI cards should align as a single row with equal size and consistent internal padding.
- The primary chart should be wider than secondary charts.
- Chart legends, axes, tooltips, and selectors require reserved internal clearance.
- Sidebar lists need consistent row height, icon column, text column, and badge alignment.
- Timeline items need a stable vertical rail and adequate text width.
- Lower cards should be treated as repeated record components, not as unrelated cards.

## Typical Before Problems This Reference Helps Repair

- KPI cards with inconsistent width, spacing, or baseline.
- Main chart squeezed by sidebar or secondary modules.
- Chart labels colliding with plot marks or legends.
- Sidebar status cards visually merging with main content.
- Recent activity rows with inconsistent icon, text, and badge alignment.
- Review cards with mismatched heights or action button drift.

## Recommended Value Profile

```json
{
  "readability": 0.85,
  "visual_impact": 0.45,
  "content_preservation": 0.9,
  "grid_strictness": 0.9,
  "editability": 0.9,
  "density": 0.75,
  "only_fix_hard_errors": 0.0
}
```

## Suggested Patch Operations

- Use `define_region` for `app_shell`, `top_bar`, `kpi_row`, `primary_chart`, `secondary_analytics`, `right_sidebar`, and `record_area`.
- Use `move_resize` to restore the 3-card KPI row and equal secondary chart modules.
- Use `align_edges` for repeated sidebar badges and list row text.
- Use `group` and `apply_auto_layout` metadata for KPI cards, activity rows, problem rows, timeline items, and review cards.
- Use `snap_to_grid` only after preserving chart label clearance.
