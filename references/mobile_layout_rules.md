# Mobile Layout Rules

Use these rules when repairing mobile UI mockups, onboarding screens, sign-in screens, list screens, or app flows. These rules are distilled from the Figma reference case in `assets/reference_cases/case_04_mobile_onboarding_wireframes/`.

## Mobile Is A Safe-Area System

Mobile repair starts with reserved system areas. Do not treat the full frame as available content.

- `status_bar`: top system area, usually 44px on the 375x812 reference.
- `home_indicator`: bottom system area, usually 34px on the 375x812 reference.
- `safe_content_area`: content area between status bar and home indicator.
- `bottom_action_area`: CTA, skip/next, or bottom navigation zone above the home indicator.

## Region Model

Use regions before moving individual nodes:

- `system_top`: status bar and top safe padding.
- `hero_media`: image, illustration, carousel image, or decorative shape.
- `title_block`: title, subtitle, and nearby paginator.
- `progress_or_pagination`: line progress, dots, or carousel indicator.
- `primary_action`: main CTA button.
- `secondary_action`: skip, sign up, secondary text button, or icon CTA.
- `bottom_system`: home indicator and bottom safe padding.

## Repair Priorities

1. Preserve status bar and home indicator clearance.
2. Keep title/subtitle together as one readable block.
3. Keep paginator visually attached to the onboarding state, not floating randomly.
4. Keep primary CTA above the home indicator with enough touch clearance.
5. Normalize touch targets to at least 44px height; prefer 52-56px for primary buttons.
6. Keep skip/next controls in predictable corners or bottom action positions.
7. Preserve carousel edge peeking when it communicates horizontal swipe.

## Common Mobile Errors

- `safe_area_violation`: content enters status bar or home indicator space.
- `cta_home_indicator_collision`: button or bottom nav is too close to the home indicator.
- `touch_target_violation`: tappable control is below usable touch size.
- `title_block_split`: title, subtitle, and paginator drift apart.
- `mobile_vertical_stack_collision`: hero, title, pagination, and CTA overlap or lose vertical rhythm.
- `carousel_peek_break`: side-peeking carousel cards are cropped or aligned in a way that no longer communicates swipe.
- `cta_priority_ambiguity`: primary and secondary actions have similar visual weight without intent.

## Value Profile Guidance

- High `readability`: preserve title/subtitle width and vertical clearance.
- High `visual_impact`: allow hero image or color field dominance, but protect CTA and safe areas.
- High `content_preservation`: keep all onboarding text and CTA labels unchanged.
- High `grid_strictness`: normalize horizontal margins, title widths, button widths, and vertical rhythm.
- High `editability`: group `title_block`, `hero_media`, `bottom_action_area`, and system bars.

## Patch Strategy

Use `define_region` for safe areas and content regions. Use `move_resize` to restore vertical stack order. Use `group` for title/subtitle/paginator and bottom action groups. Use `set_constraints` for bottom nav or CTA containers pinned above the home indicator. Use `apply_auto_layout` metadata for stacked buttons.

## Pattern-Specific Rules

### Auth/Form Screens

Use when a screen includes sign-in, sign-up, password recovery, verification, social login, or a bottom-sheet form.

- Keep `form_group` as a vertical stack with equal field widths and stable field height.
- Keep label, input, helper text, and error text attached to the same field.
- Keep primary CTA below the final required field, with 16-24px separation.
- Keep social login actions as a separate secondary group after the primary auth action.
- Keep account-switch text near the bottom but above the home indicator.
- In bottom sheets, preserve handle, title, form fields, helper text, and CTA order.

Common errors: `form_field_stack_drift`, `social_login_detachment`, `bottom_sheet_compression`, `cta_priority_ambiguity`.

### Profile/Gallery Screens

Use when a screen contains avatar, name, handle, bio, stats, follow/message actions, tabs, gallery grid, collections, or activity lists.

- Keep avatar, name, handle, and bio as a `profile_header` region.
- Keep stats in one row with equal columns and shared label/value baselines.
- Keep follow/message buttons close to the profile identity they affect.
- Keep gallery tiles on a consistent grid; crop differences are allowed only when intentional masonry is clear.
- Keep profile tabs attached to the content grid/list below.

Common errors: `profile_header_split`, `profile_stats_drift`, `gallery_grid_break`, `floating_action_overlap`.

### Media Player Screens

Use when a screen contains artwork, track/video metadata, playback controls, progress line, lyrics, queue, album cards, or media editing controls.

- Give artwork a stable dominant region without forcing controls into unsafe areas.
- Keep track title, artist, and metadata as one text block.
- Keep progress track, progress handle, elapsed time, and duration aligned.
- Center primary playback control; distribute secondary controls symmetrically.
- Keep sticky controls separate from lyrics, queue rows, or editor tools.

Common errors: `media_artwork_squeeze`, `media_progress_detachment`, `media_control_misalignment`, `lyrics_control_collision`.

### E-commerce Screens

Use when a screen contains product cards, product detail, image carousel, price, variants, filter sheet, cart rows, checkout summary, promo carousel, or add-to-cart/checkout CTA.

- Keep product image, title, price, rating, and badge as one `product_card` unit.
- Keep two-column product grids equal in width and gutter unless a hero product is intentional.
- Keep sticky add-to-cart or checkout CTA above the home indicator.
- Keep cart rows aligned by image, product text, quantity control, price, and delete action.
- Keep checkout summary visually separate from cart item rows.
- Keep filter controls grouped by category inside a bottom sheet or panel.

Common errors: `product_grid_drift`, `product_info_detachment`, `cart_row_misalignment`, `checkout_sheet_collision`, `filter_sheet_overflow`.

### Travel/Booking Screens

Use when a screen contains destination discovery, search fields, origin/destination pairs, date selectors, passenger selectors, result lists, filters, itinerary summary, or booking/payment forms.

- Keep origin/destination/date/passenger fields in readable groups.
- Preserve paired fields as pairs; do not distribute them like unrelated cards.
- Keep result cards scanable by aligning provider, time, location, price, and action.
- Keep itinerary summary and final booking CTA separated.
- Keep filter chips and sorting controls close to result lists.

Common errors: `booking_field_pair_drift`, `result_card_alignment_drift`, `filter_chip_wrap_break`, `booking_cta_collision`.

### Health/Data Screens

Use when a screen contains health metrics, activity charts, nutrition logs, doctor/service cards, appointment rows, or article lists inside a health app.

- Keep metric cards comparable with equal width, height, and label/value baselines.
- Keep chart labels, legends, and units clear of bars, rings, and plot edges.
- Keep service icons attached to labels in a stable grid.
- Keep doctor rows grouped by avatar, name, specialty, rating/time, and action.
- Keep nutrition rows aligned by food name, serving detail, quantity, and calorie values.

Common errors: `health_metric_grid_drift`, `mobile_chart_label_collision`, `service_grid_break`, `nutrition_row_misalignment`.

### Social/Messaging Screens

Use when a screen contains chat list, message thread, input bar, comments, social feed, video call grid, rooms, or call history.

- Keep chat list rows aligned by avatar, title, preview, time, and unread marker.
- Keep message bubbles on their sender/receiver axis; preserve grouped bubble spacing.
- Keep message input bar pinned above the home indicator and separated from messages.
- Keep video call participant tiles in a stable grid and controls in a bottom action strip.
- Keep comment rows distinct from reply CTAs and sticky actions.

Common errors: `message_axis_crossing`, `chat_input_collision`, `chat_row_alignment_drift`, `video_call_control_overlap`.

### Feed/News Screens

Use when a screen contains featured story, article card, category rail, editorial carousel, author row, date, body text, or related article list.

- Keep article image, label, title, date, and author as a readable editorial unit.
- Preserve carousel edge-peeking when it signals horizontal browsing.
- Keep title text legible over or below media; do not let image dominance destroy reading.
- Keep long-form body text clear of author/action rows and tab bars.
- Keep category controls visually attached to the list they filter.

Common errors: `article_unit_detachment`, `editorial_title_collision`, `author_row_detachment`, `category_control_detachment`.

### Settings/Account Screens

Use when a screen contains profile/account header, grouped settings rows, dividers, toggles, chevrons, tab bar, logout/destructive action, or settings modal.

- Keep row height consistent; 52-64px is typical for mobile settings rows.
- Align icon, label, value, toggle, and chevron to a shared row axis.
- Keep dividers inside the row group bounds, not full-screen unless intentionally table-like.
- Keep section headers close to the row group they label.
- Keep destructive/logout actions visually distinct from ordinary navigation rows.
- Keep modal settings panels separated from the underlying screen.

Common errors: `settings_row_axis_drift`, `divider_boundary_break`, `section_header_detachment`, `destructive_action_ambiguity`, `modal_panel_blend`.
