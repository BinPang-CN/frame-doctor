---
name: frame-doctor
description: 当用户已有 Figma frame、PPT slide、UI mockup、dashboard 或信息图画布，且元素已经生成但出现重叠、越界、间距混乱、对齐失败、文本溢出或视觉层级不清时使用。本 Skill 不从零生成设计，不改写内容，不替用户决定审美方向；它通过布局诊断、语义角色确认、结构候选、人类价值选择、布局补丁和复检报告，将人工拖拽修图重构为可验证的人机协作流程。
---

# Frame Doctor

## Mission

Use Frame Doctor as the executable Skill implementation of LDS: Layout Decision System. Repair spatial relationships in an existing canvas after elements already exist. Fix geometry, grouping, spacing, alignment, hierarchy clarity, and text box fit. Do not generate new content, rewrite copy, redesign the visual style, or replace assets.

Core statement: "We are not doing automatic layout. We are redistributing layout decision power."

## When to Use

Use this skill when all of these are true:

- The user has an existing canvas such as a Figma frame, PPT slide, UI mockup, dashboard, or infographic.
- The canvas already contains nodes or design elements.
- The problem is overlap, out-of-bounds placement, text overflow, spacing violation, alignment drift, unclear hierarchy, or a similar layout conflict.

For JSON-based MVP work, use the bundled scripts:

- `scripts/detect_layout_errors.py` to detect objective conflicts.
- `scripts/score_layout.py` to score a canvas.
- `scripts/propose_layout_patch.py` to propose a value-aware patch.
- `scripts/apply_patch_to_json.py` to apply a patch.
- `scripts/audit_layout.py` to compare before and after canvases.
- `scripts/run_demo.py` to run the full before/after loop.

## When Not to Use

Do not use this skill for:

- Generating a design from zero.
- Rewriting or shortening text.
- Rebranding or changing visual identity.
- Generating illustrations or imagery.
- Pure aesthetic advice without a structured layout patch.

## Core Principle

Separate three kinds of decisions:

1. Objective geometry: detect machine-verifiable problems such as overlap, out-of-bounds nodes, margin breach, spacing violations, alignment drift, and text overflow.
2. Structural interpretation: propose candidate structures such as `two_column`, `card_grid`, `dashboard`, `mobile_screen`, `mobile_onboarding`, `mobile_auth_form`, `mobile_profile_grid`, `mobile_media_player`, `mobile_ecommerce_flow`, `mobile_booking_flow`, `mobile_health_dashboard`, `mobile_social_messaging`, `mobile_feed_news`, `mobile_settings_account`, `comparison`, `process_pipeline`, `layered_system_graph`, or grid-based variants.
3. Value judgment: ask the human to choose priorities such as readability, visual impact, density, content preservation, semantic fidelity, grid strictness, editability, and minimal-fix behavior.

Never collapse these into one silent decision. Geometry can be detected automatically; structure can be recommended; value priorities must be confirmed unless the user explicitly asks for automatic mode.

## LDS Architecture Mapping

Frame Doctor maps LDS into five executable layers.

### L0 Conflict Detection

Detect objective and semi-objective layout conflicts before choosing a repair:

- overlap
- out-of-bounds
- text overflow
- margin breach
- spacing violation
- alignment drift
- column drift
- gutter anomaly
- baseline mismatch when metadata exists
- image-caption detachment
- semantic uncertainty
- hierarchy ambiguity

Use `scripts/detect_layout_errors.py` and `references/layout_error_taxonomy.md`.

### L1 Structure Hypothesis

Generate multiple candidate structures unless the user or canvas has already fixed the structure. Do not output one silent answer when meaningful alternatives exist.

Examples include `two_column`, `hero_plus_support`, `card_grid`, `dashboard`, `operational_dashboard`, `mobile_screen`, `mobile_onboarding`, `mobile_auth_form`, `mobile_ecommerce_flow`, `process_pipeline`, and `layered_system_graph`.

Use `scripts/propose_layout_patch.py` and `references/layout_patterns.md`.

### L2 Human Value Function

Ask for or load human priorities before repair unless automatic mode is explicit. Use these value profile keys:

- `readability`
- `visual_impact`
- `density`
- `grid_strictness`
- `editability`
- `content_preservation`
- `semantic_fidelity`
- `only_fix_hard_errors`

Use `scripts/value_function.py` and `references/value_profile.md`. High `only_fix_hard_errors` means preserve the existing layout and only repair critical objective conflicts.

### L3 Constraint Execution

Emit a structured, reversible JSON patch using operations from `references/patch_schema.md`. Preserve text, images, brand style, semantic meaning, and editability. Use grouping, constraints, Auto Layout metadata, `snap_to_grid`, `pair_caption_image`, `define_region`, and `route_connectors` when appropriate.

### L4 Audit Loop

Compare before and after. Report conflict reduction, overlap area reduction, overflow reduction, alignment improvement, grid snap improvement where available, hierarchy clarity, layout stability, and remaining critical issues.

Use `scripts/audit_layout.py` and `scripts/run_demo.py`.

## Workflow

1. Canvas Intake: inspect frame size, nodes, roles, bounds, text fields, and metadata.
2. Conflict Detection: run objective checks and produce a conflict report.
3. Semantic Role Map: map each node to a role, marking low-confidence roles as `unknown` or tentative.
4. Structure Candidates: propose at least two viable layout patterns when the structure is not already fixed.
5. Human Value Profile: confirm or choose a profile before repair unless automatic mode is explicit.
6. Layout Patch: output a structured JSON patch with reversible operations.
7. Audit Report: compare before/after scores, metric deltas, layout stability, and remaining conflicts.

## Human-in-the-loop Rules

- Ask the user when semantic roles are uncertain and affect layout.
- Provide at least two layout candidates before committing to a structure, unless the user provides a fixed structure.
- Do not silently decide value priority. Confirm a value profile before repair unless the user asks for automatic mode.
- Preserve user content and intent even when an alternate layout would look cleaner.

## Output Contract

Every Frame Doctor run should output:

1. Layout Conflict Report
2. Semantic Role Map
3. Structure Candidates
4. Human Value Profile
5. Layout Patch
6. Layout QA Report

For JSON-based repairs, keep patches compatible with `references/patch_schema.md`.

## Hard Rules

- Do not delete content.
- Do not rewrite text.
- Do not replace images.
- Do not change brand colors, fonts, or visual style.
- Do not flatten editable layers.
- Do not output pure aesthetic commentary; always produce a structured patch.

## References

- Read `references/layout_error_taxonomy.md` when classifying conflicts.
- Read `references/layout_patterns.md` when choosing structure candidates.
- Read `references/grid_constraints.md` when grid, margins, columns, gutters, baseline rhythm, or image-caption anchoring matter.
- Read `references/dashboard_layout_rules.md` when repairing dashboard, analytics, admin, KPI, chart, table, activity feed, or right-sidebar layouts.
- Read `references/mobile_layout_rules.md` when repairing mobile UI mockups, onboarding, auth forms, profile/gallery, media player, e-commerce, booking/travel, health/data, social/messaging, feed/news, settings/account, bottom navigation, safe area, CTA, or mobile list/card layouts.
- Read `references/semantic_role_map.md` when assigning or confirming node roles.
- Read `references/value_profile.md` when choosing repair priorities.
- Read `references/repair_rules.md` before proposing a patch.
- Read `references/patch_schema.md` before applying or emitting patch JSON.
- Read `assets/reference_cases/*/notes.md` when repairing similar complex process, mechanism, or graph-interaction slides.
