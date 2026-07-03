# Dashboard Layout Rules

Use these rules when repairing operational dashboards, analytics screens, admin dashboards, or data-heavy product pages. These rules are distilled from the Figma reference case in `assets/reference_cases/case_03_dashboard_data_page/`.

## Dashboard Is A Work Surface

A dashboard should feel quiet, scannable, and repeatable. Do not repair it like a marketing slide. Favor dense but calm information hierarchy, stable regions, and predictable repeated components.

## Region Model

Use regions before moving individual modules:

- `app_shell`: persistent navigation, logo, app menu, and footer utility links.
- `top_bar`: page title, subtitle, alerts, account controls, and search.
- `kpi_row`: top summary cards with equal width and shared baseline.
- `primary_chart`: the largest chart; it anchors the main analytic story.
- `secondary_analytics`: supporting bar, pie, table, or comparison modules.
- `right_sidebar`: status, problems, activity, timeline, or secondary operational feed.
- `review_or_table_area`: lower repeated records, comments, tasks, or table rows.

## Repair Priorities

1. Protect the app shell and top bar.
2. Keep the KPI row above the main chart.
3. Give the primary chart the largest content area and a stable aspect ratio.
4. Keep secondary charts in equal-width modules below the primary chart.
5. Keep the right sidebar independent from the main content column.
6. Normalize repeated list rows, activity items, review cards, badges, and chart labels.
7. Preserve chart legends, axes, labels, and tooltips; do not treat them as decoration.

## Common Dashboard Errors

- `kpi_grid_drift`: KPI cards differ in width, height, or vertical baseline.
- `chart_axis_collision`: axes, labels, legends, or tooltips collide with plot marks.
- `sidebar_collision`: right sidebar content overlaps, crowds, or visually merges with main content.
- `chart_hierarchy_ambiguity`: too many charts have equal size and compete for primary attention.
- `activity_feed_compression`: timeline or activity rows are packed too tightly to scan.
- `badge_alignment_drift`: status badges in list rows fail to align to a common right edge.

## Value Profile Guidance

- High `readability`: increase row height, chart label clearance, and list item spacing.
- High `grid_strictness`: normalize KPI cards, chart cards, right rail widths, and repeated records.
- High `density`: keep the dashboard compact, but preserve minimum chart and table label clearance.
- High `editability`: use region metadata, grouped cards, repeated row groups, and Auto Layout metadata.
- High `visual_impact`: allow the primary chart to dominate, not the KPI cards or sidebar.

## Patch Strategy

Use `define_region` for the app shell, top bar, content lane, KPI row, primary chart, secondary analytics, and right sidebar. Use `move_resize` to normalize card geometry. Use `group` for repeated KPI cards, chart cards, list rows, and timeline items. Use `apply_auto_layout` metadata on rows and sidebars. Use `align_edges` for badges and row labels.
