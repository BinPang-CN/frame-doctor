# Repair Rules

Frame Doctor repairs layout without changing design intent.

## Required Principles

- Preserve all content.
- Preserve visual style, including colors, fonts, imagery, and brand treatment.
- Fix objective geometry errors before subjective refinements.
- Group related nodes before aligning them.
- Normalize same-type repeated components to consistent dimensions when roles match.
- Treat margins, columns, gutters, fields, and baselines as layout constraints when the canvas declares or implies a grid.
- Keep image-caption pairs spatially attached before optimizing other local spacing.
- Prefer Auto Layout metadata where the target tool supports it.
- Ask the user before resolving uncertain semantics that affect the layout.
- Audit after repair and report remaining issues.

## Operation Selection

- Use `move_resize` for objective overlap, bounds, and sizing fixes.
- Use `group` to preserve relationship between related nodes such as card children or image caption pairs.
- Use `apply_auto_layout` as metadata in the JSON MVP; do not call external APIs.
- Use `normalize_spacing` and `align_edges` for repeated elements.
- Use `resize_text_box` when text likely overflows but the text content must remain unchanged.
- Use `snap_to_grid` when edges are close to a declared grid but visually drift.
- Use `pair_caption_image` when a caption belongs to a nearby image or chart but is detached.
- Use `define_region` before repairing complex mechanism slides with stacked graph/process/sidebar/legend areas.
- Use `route_connectors` when lines or arrows cross through cards, text, icons, or graph labels.
- For mobile screens, define `system_top`, `system_bottom`, `title_block`, and `bottom_action_area` before moving CTA or nav controls.
- Keep tappable controls at least 44px high; prefer 52-56px for primary mobile buttons.
- For auth screens, group `form_group` before aligning CTAs or social login actions.
- For profile screens, group `profile_header`, then normalize `stats_row` and `gallery_grid`.
- For media screens, align `progress_line` and `media_controls` as functional controls before balancing artwork.
- For e-commerce screens, keep `product_card`, `cart_item`, and `checkout_summary` intact before moving sticky CTAs.
- For booking screens, keep `booking_field_pair` and `itinerary_summary` relationships intact.
- For health dashboards, protect metric comparability and chart label clearance before visual polish.
- For messaging screens, preserve sender/receiver axes and pin `message_input` above the home indicator.
- For feed/news screens, preserve article image-title-author/date grouping and intentional carousel peeking.
- For settings screens, normalize row axes and divider boundaries before adjusting section spacing.

## Grid-aware Execution Order

1. Resolve out-of-bounds and hard overlaps.
2. Normalize margins and type area.
3. Infer or apply grid family: simple column grid, 8-field, 20-field, or 32-field modular grid.
4. Assign semantic roles to modules.
5. Define major regions for complex process or graph interaction slides.
6. Normalize gutters and repeated component sizes.
7. Pair images/charts with captions.
8. Route connectors around content bodies and record legend semantics.
9. Align text rhythm where baseline metadata exists.
10. Group editable structures.
11. Run audit and list remaining issues.

## Mobile Execution Order

1. Define `status_bar`, `home_indicator`, and usable `safe_content_area`.
2. Identify page subtype: onboarding, auth/form, profile/grid, media player, e-commerce, booking, health/data, social/messaging, feed/news, or settings/account.
3. Group subtype-critical regions before moving individual nodes.
4. Resolve hard overlaps and home-indicator collisions.
5. Normalize repeated modules such as form fields, product cards, settings rows, chat rows, or metric cards.
6. Align functional controls such as CTA, media controls, filters, toggles, and message input bars.
7. Preserve intentional scroll or carousel overflow while fixing accidental out-of-bounds content.
8. Re-audit touch targets, safe-area clearance, and content group attachment.

## Safety Rules

Never use a repair to delete content, rewrite text, replace images, change brand style, or flatten editable layers.
