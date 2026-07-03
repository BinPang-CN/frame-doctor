# Frame Doctor

Frame Doctor is the executable Skill package for LDS: Layout Decision System. It repairs layout geometry after an AI-generated canvas already contains elements. It focuses on overlaps, out-of-bounds nodes, text overflow, spacing issues, alignment drift, inconsistent groups, unclear hierarchy, and value-aware repair decisions.

LDS is not an automatic layout beautifier. It turns layout repair into a decision process: detect conflicts, propose structure hypotheses, rank them with a human value function, execute reversible constraints, and audit the result.

> We are not doing automatic layout. We are redistributing layout decision power.

The project also includes a lightweight grid-constraint layer distilled from a local LDS Grid Reference Pack. That layer treats margins, columns, gutters, fields, baselines, and image-caption anchoring as measurable repair constraints rather than decorative style advice.

## Why This Is Not a Generic Layout Assistant

Frame Doctor does not generate a design from scratch, rewrite copy, replace images, or choose a new style. It treats layout repair as a post-processing workflow: detect conflicts, map semantic roles, propose structure candidates, confirm a value profile, emit a patch, apply it, and audit the result.

## LDS Implementation Layers

- L0 Conflict Detection: `scripts/detect_layout_errors.py` detects overlap, out-of-bounds, text overflow, margin breach, spacing violation, alignment drift, gutter anomaly, column drift, baseline mismatch, image-caption detachment, semantic uncertainty, and hierarchy ambiguity.
- L1 Structure Hypothesis: `scripts/propose_layout_patch.py` proposes multiple candidate structures such as `two_column`, `card_grid`, `dashboard`, `mobile_screen`, `process_pipeline`, and `layered_system_graph`.
- L2 Human Value Function: `scripts/value_function.py` ranks candidates using readability, visual impact, density, grid strictness, editability, content preservation, semantic fidelity, and minimal-fix preference.
- L3 Constraint Execution: `scripts/apply_patch_to_json.py` applies reversible JSON patch operations while rejecting forbidden content/style operations.
- L4 Audit Loop: `scripts/audit_layout.py` compares before/after score, conflicts, overlap area, overflow distance, alignment drift, grid snap error, hierarchy clarity, layout stability, and remaining conflicts.

## Skill Trigger Scenarios

Use this skill when a Figma frame, PPT slide, UI mockup, dashboard, or infographic already exists and the generated nodes are spatially broken. Good triggers include overlap, out-of-bounds placement, text overflow, spacing violation, alignment drift, unclear hierarchy, and repeated components with inconsistent size.

## File Structure

```text
frame-doctor/
├── SKILL.md
├── README.md
├── references/
├── scripts/
├── assets/
│   ├── demo_cases/
│   ├── reference_cases/
│   ├── value_profiles/
│   └── expected_outputs/
├── tests/
└── .gitignore
```

## Run the Demo

From the project directory:

```bash
python scripts/run_demo.py assets/demo_cases/case_01_ppt_content_before.json --profile assets/value_profiles/readability_first.json
```

Other useful commands:

```bash
python scripts/detect_layout_errors.py assets/demo_cases/case_01_ppt_content_before.json
python scripts/score_layout.py assets/demo_cases/case_01_ppt_content_before.json
python scripts/propose_layout_patch.py assets/demo_cases/case_01_ppt_content_before.json --profile assets/value_profiles/readability_first.json
python scripts/apply_patch_to_json.py assets/demo_cases/case_01_ppt_content_before.json patch.json --output repaired.json
python scripts/audit_layout.py assets/demo_cases/case_01_ppt_content_before.json repaired.json
python scripts/propose_layout_patch.py assets/demo_cases/case_01_ppt_content_before.json --profile assets/value_profiles/density_first.json
python scripts/propose_layout_patch.py assets/demo_cases/case_01_ppt_content_before.json --profile assets/value_profiles/minimal_fix.json
```

`apply_patch_to_json.py` accepts either a raw patch JSON or a proposal JSON that contains `recommended_patch`.

## Visual Reference Cases

`assets/reference_cases/` contains before/after PNG pairs and notes for complex slide repairs:

- `case_01_shopping_dual_task_pipeline`: process explanation slide with pipeline, Goal State mechanism, task sidebar, and training output.
- `case_02_goal_state_graph_interaction`: layered graph interaction slide with top graph, middle process flow, bottom graph, right result sidebar, and legend.
- `case_03_dashboard_data_page`: Figma dashboard reference with app shell, KPI row, primary chart, secondary analytics, right sidebar, activity feed, and review cards.
- `case_04_mobile_onboarding_wireframes`: Figma mobile onboarding wireframe reference with safe areas, hero media, title blocks, pagination, CTA hierarchy, and home indicator constraints.
- `case_05_mobile_auth_forms`: mobile sign-in/sign-up, form stack, social login, and bottom-sheet auth patterns.
- `case_06_mobile_profile_grid`: profile header, stats row, action buttons, gallery grid, and collection/list patterns.
- `case_07_mobile_media_player`: artwork, metadata, progress line, playback controls, lyrics, queue, and media detail patterns.
- `case_08_mobile_ecommerce_flow`: product grid/detail, cart, checkout summary, filter sheet, promo carousel, and sticky CTA patterns.
- `case_09_mobile_travel_booking`: travel discovery, search fields, result cards, filters, itinerary summary, and booking form patterns.
- `case_10_mobile_health_dashboard`: health metric cards, activity charts, service grids, doctor rows, nutrition logs, and data-card patterns.
- `case_11_mobile_social_messaging`: chat list/thread, input bar, comments, video call, rooms, and social feed patterns.
- `case_12_mobile_feed_news`: featured story, article card, category rail, editorial carousel, author row, and long-form reading patterns.
- `case_13_mobile_settings_account`: account/profile header, settings rows, dividers, toggles, tab bar, modal settings panel, and destructive actions.

Use these as pattern references for complex mechanism slides, operational dashboards, and mobile UI mockups; they are not JSON demos and do not require external APIs.

## Run Tests

```bash
python -m unittest discover -s tests
```

## MVP Limits

- JSON only; no Figma API, PPT API, or external network calls.
- Rule-based repair; no visual rendering or screenshot verification.
- Auto Layout is stored as metadata instead of being applied through a design tool API.
- Text overflow is estimated from box size and character count.
- Structural candidates are heuristic and should be confirmed by a human for real design work.
- Detector heuristics are deterministic and lightweight; they are intended for repair triage, not pixel-perfect design-tool validation.
- Grid checks are intentionally lightweight; declared safe margins are detected, while full baseline and inferred modular-grid scoring remain future work.

## Future Integrations

- Figma: map canvas JSON to frame/node data, apply supported patch operations through plugin APIs, and audit with rendered bounds.
- PPT: convert slide shapes to canvas JSON, apply geometry repairs, and write back to `.pptx`.
- LearnBuddy: wrap the workflow as a guided skill that asks for value profiles and presents before/after reports.
- Ardot: connect patch output to Ardot's design execution layer while preserving the same operation schema.
