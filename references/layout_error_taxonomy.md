# Layout Error Taxonomy

Frame Doctor classifies layout errors by evidence and repair urgency.

## Critical

Critical errors make the canvas materially unusable or likely broken in export.

- `overlap`: Two visible nodes occupy the same area in a way that blocks content or interaction.
- `out_of_bounds`: A node extends beyond the frame edge.
- `text_overflow`: Text content likely cannot fit inside its text box.
- `margin_breach`: A node enters a declared safe margin or violates the type area.
- `title_wrapping`: A title wraps, collides, or breaks in a way that destroys title meaning or page entry.

## Warning

Warning errors reduce clarity, scanability, or editability but may be acceptable in some expressive layouts.

- `spacing_violation`: Related or adjacent nodes are closer than the minimum intended spacing.
- `alignment_drift`: Nodes that appear to belong to a row, column, or group do not share a consistent edge or center.
- `column_drift`: Nodes intended to share a column do not align to the inferred column edge or center.
- `gutter_anomaly`: Spacing between repeated modules is inconsistent or below the chosen gutter.
- `baseline_mismatch`: Text nodes that should share typographic rhythm do not align to a baseline grid.
- `image_caption_detachment`: A caption is too far from, misaligned with, or visually detached from its image/chart.
- `connector_clutter`: Lines or arrows cross through text, icons, cards, or too many relationship types compete without routing discipline.
- `region_boundary_failure`: Distinct semantic regions such as graph layer, process row, sidebar, legend, or output area blend together.
- `reading_path_break`: The intended reading path is interrupted by overlaps, competing focal points, or line crossings.
- `kpi_grid_drift`: KPI cards differ in size, baseline, internal padding, or row alignment.
- `chart_axis_collision`: Chart axes, labels, legends, selectors, or tooltips collide with plot content or card edges.
- `sidebar_collision`: Right sidebar content visually merges with or crowds the main dashboard content.
- `activity_feed_compression`: Timeline or activity rows are too compressed for scanning.
- `badge_alignment_drift`: Status badges in repeated rows do not align to a common edge.
- `safe_area_violation`: Mobile content enters the status bar, home indicator, notch, or reserved system area.
- `cta_home_indicator_collision`: CTA, bottom nav, or bottom action group is too close to or overlaps the home indicator.
- `touch_target_violation`: Interactive control is below usable touch target size or has insufficient tap spacing.
- `title_block_split`: Mobile title, subtitle, and paginator no longer read as one grouped message.
- `mobile_vertical_stack_collision`: Hero, title, pagination, content, and CTA collide or lose vertical rhythm.
- `carousel_peek_break`: Side-peeking carousel cards are cropped or aligned in a way that no longer communicates horizontal swipe.
- `cta_priority_ambiguity`: Primary and secondary actions have unclear visual priority.
- `form_field_stack_drift`: Form fields, labels, helper text, or CTA no longer share a stable vertical stack.
- `social_login_detachment`: Social login actions are visually detached from the auth flow or confused with primary CTA.
- `bottom_sheet_compression`: A modal or bottom sheet compresses title, fields, helper text, or CTA into an unreadable stack.
- `profile_header_split`: Avatar, name, handle, bio, or profile action no longer read as one identity region.
- `profile_stats_drift`: Profile stats lose equal columns, shared baselines, or comparable spacing.
- `gallery_grid_break`: Gallery or media grid gutters, tile sizing, or crop rhythm break unintentionally.
- `floating_action_overlap`: Profile, media, or product floating action overlaps content it should control.
- `media_artwork_squeeze`: Media artwork dominates or collapses in a way that damages controls or metadata.
- `media_progress_detachment`: Progress handle, track, elapsed time, or duration detach from each other.
- `media_control_misalignment`: Playback or media control icons lose center alignment, symmetry, or touch spacing.
- `lyrics_control_collision`: Lyrics, queue, captions, or transcript content collides with sticky media controls.
- `product_grid_drift`: Product cards lose equal width, gutter, image ratio, or row rhythm.
- `product_info_detachment`: Product image, title, price, rating, or CTA no longer read as one product unit.
- `cart_row_misalignment`: Cart item image, title, quantity, price, and delete/action columns do not align.
- `checkout_sheet_collision`: Checkout summary, cart content, or CTA collides with a bottom sheet or home indicator.
- `filter_sheet_overflow`: Filter controls overflow or compress inside a sheet or panel.
- `booking_field_pair_drift`: Paired travel/booking fields such as origin/destination or dates separate or misalign.
- `result_card_alignment_drift`: Search/travel/result card metadata such as price, time, provider, or action loses scan alignment.
- `filter_chip_wrap_break`: Filter chips wrap or overflow without stable row rhythm.
- `booking_cta_collision`: Booking or reservation CTA collides with summary content or bottom safe area.
- `health_metric_grid_drift`: Health metric cards lose comparable sizing, label/value baselines, or spacing.
- `mobile_chart_label_collision`: Mobile chart labels, units, axes, legends, or values collide with chart marks.
- `service_grid_break`: Service icon/label grid loses row/column consistency.
- `nutrition_row_misalignment`: Food/nutrition rows misalign item name, serving info, quantity, or calorie values.
- `message_axis_crossing`: Chat bubbles cross sender/receiver alignment axes or group incorrectly.
- `chat_input_collision`: Message input/composer collides with messages, keyboard area, or home indicator.
- `chat_row_alignment_drift`: Conversation rows lose avatar, title, preview, time, or unread marker alignment.
- `video_call_control_overlap`: Call controls overlap participant tiles or unsafe bottom region.
- `article_unit_detachment`: Article image, label, title, date, source, or author row visually detach.
- `editorial_title_collision`: News/feed title collides with image, controls, or unreadable background.
- `author_row_detachment`: Author/source/date/action row separates from its article.
- `category_control_detachment`: Category control, tab, or filter rail is detached from the list it controls.
- `settings_row_axis_drift`: Settings row icon, label, value, toggle, or chevron no longer share a row axis.
- `divider_boundary_break`: Dividers extend beyond or detach from their row group boundaries.
- `section_header_detachment`: A section header floats too far from its settings/list group.
- `destructive_action_ambiguity`: Logout/delete/destructive action looks like an ordinary row or primary CTA.
- `modal_panel_blend`: Modal, side panel, or settings overlay blends into underlying content.
- `inconsistent_group_size`: Repeated components such as cards or KPI tiles have mismatched dimensions without semantic reason.
- `hierarchy_ambiguity`: Size, position, or grouping fails to make the primary content clear.

## Uncertain

Uncertain errors need human confirmation or a semantic role check before repair.

- `semantic_role_uncertainty`: A node's role is missing, conflicting, or low-confidence.
- `hierarchy_ambiguity`: Treat as uncertain when the geometry alone does not prove which element should dominate.

## Reporting Rules

Each reported error should include:

- `type`: machine-readable error type.
- `severity`: `critical`, `warning`, or `uncertain`.
- `nodes`: node ids involved.
- `message`: short human-readable explanation.
- `metrics`: numbers used for detection, such as overlap area or overflow distance.
