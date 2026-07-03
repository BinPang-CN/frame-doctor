# Layout Patterns

Use layout patterns as structure candidates, not as absolute design commands.

## two_column

- Applicable when: A slide or page contains a title plus body content and a supporting image, chart, or media element.
- Typical nodes: `title`, `subtitle`, `body`, `image`, `caption`, `button`.
- Prioritize fixing: overlap between text and media, reading order, title alignment, caption attachment.
- Risks: narrow columns can create text overflow; image crop may need manual review.

## hero_plus_support

- Applicable when: One primary message or visual needs dominance with supporting proof points below or beside it.
- Typical nodes: `title`, `subtitle`, `image`, `body`, `button`, `caption`.
- Prioritize fixing: unclear hierarchy, title/media competition, call-to-action alignment.
- Risks: can over-emphasize visual impact and reduce dense information capacity.

## card_grid

- Applicable when: Four or more repeated cards, feature blocks, KPI tiles, or content modules are present.
- Typical nodes: `card`, `title`, `body`, `image`, `caption`, `button`.
- Prioritize fixing: inconsistent group size, spacing violation, row/column alignment.
- Risks: rigid grids can hide intended emphasis or make content feel uniform.

## dashboard

- Applicable when: A data-oriented frame contains KPI cards, filters, charts, tables, or a header.
- Typical nodes: `navigation`, `title`, `kpi_card`, `chart`, `filter`, `sidebar`, `activity_feed`, `timeline`, `table`, `review_card`.
- Prioritize fixing: app shell separation, KPI row alignment, primary chart dominance, chart label clearance, right sidebar independence, repeated row/card normalization.
- Risks: aggressive normalization can reduce useful dashboard density; treating chart labels, legends, tooltips, or axes as decoration can break data meaning.

## operational_dashboard

- Applicable when: A long-form admin dashboard has a left app shell, top bar, KPI cards, primary chart, secondary analytics, right sidebar, activity/timeline, and lower records.
- Typical nodes: `app_shell`, `top_bar`, `kpi_card`, `primary_chart`, `secondary_chart`, `right_sidebar`, `status_panel`, `activity_feed`, `timeline`, `review_card`.
- Prioritize fixing: region separation, 3/4-card KPI grid, main chart aspect ratio, secondary chart equality, sidebar list row alignment, timeline rail stability.
- Risks: over-spacious repair can hurt operational density; overly dense repair can make chart labels and activity text unreadable.

## mobile_screen

- Applicable when: Frame dimensions resemble a phone screen or nodes include mobile navigation, search, tabs, cards, or bottom navigation.
- Typical nodes: `status_bar`, `title`, `subtitle`, `search`, `tabs`, `card`, `button`, `bottom_nav`, `home_indicator`.
- Prioritize fixing: safe-area clearance, vertical stacking, bottom navigation bounds, touch target size, tappable spacing, card overlap.
- Risks: limited height may require scrolling; do not delete content to force fit.

## mobile_onboarding

- Applicable when: A mobile screen contains hero media, onboarding title/subtitle, paginator/progress, skip/next controls, primary CTA, or sign-in/sign-up action stack.
- Typical nodes: `status_bar`, `home_indicator`, `hero_media`, `title_block`, `pagination`, `primary_button`, `secondary_button`, `bottom_action`.
- Prioritize fixing: safe-area protection, title block grouping, CTA/home indicator clearance, button hierarchy, paginator attachment, carousel edge-peek preservation.
- Risks: centering every element can destroy carousel swipe affordance; hero media should not squeeze title or CTA into unsafe areas.

## mobile_auth_form

- Applicable when: A mobile screen contains sign-in, sign-up, password recovery, verification, social login, form fields, or a form bottom sheet.
- Typical nodes: `status_bar`, `title_block`, `form_group`, `form_field`, `primary_button`, `secondary_button`, `social_login`, `bottom_sheet`, `home_indicator`.
- Prioritize fixing: field stack alignment, label/helper attachment, CTA priority, social login grouping, bottom-sheet compression, home indicator clearance.
- Risks: widening every input can damage intentional modal/sheet hierarchy; keep legal/helper text attached to the action it qualifies.

## mobile_profile_grid

- Applicable when: A mobile screen contains avatar, name, handle, bio, stats, tabs, gallery grid, follow/message buttons, collections, or profile activity.
- Typical nodes: `profile_header`, `avatar`, `stats_row`, `profile_action`, `tabs`, `gallery_grid`, `media_tile`, `bio`, `list_item`.
- Prioritize fixing: avatar/name grouping, stats comparability, action proximity, grid gutters, tab/content attachment.
- Risks: equalizing media tiles can destroy intentional masonry; preserve media crops when they carry content meaning.

## mobile_media_player

- Applicable when: A mobile screen contains artwork, track/video title, artist metadata, progress line, playback controls, lyrics, queue, album cards, or editor controls.
- Typical nodes: `media_artwork`, `media_metadata`, `progress_line`, `media_controls`, `lyrics`, `queue_row`, `tab_bar`.
- Prioritize fixing: artwork/control separation, metadata grouping, progress handle alignment, playback control symmetry, sticky control clearance.
- Risks: making artwork too large can push functional controls below safe areas; never treat control icons as decoration.

## mobile_ecommerce_flow

- Applicable when: A mobile screen contains catalog/product grid, product detail, price, rating, variants, cart, checkout, filter sheet, promo carousel, or sticky add-to-cart CTA.
- Typical nodes: `product_card`, `product_image`, `price`, `rating`, `variant_selector`, `cart_item`, `checkout_summary`, `filter_sheet`, `primary_button`.
- Prioritize fixing: product card consistency, image/title/price pairing, cart row columns, checkout CTA clearance, filter group containment.
- Risks: overemphasizing promotional media can reduce conversion clarity; preserve price and CTA scanability.

## mobile_booking_flow

- Applicable when: A mobile screen contains travel search, origin/destination/date fields, filter chips, result cards, itinerary summary, or booking/passenger/payment forms.
- Typical nodes: `search_field`, `booking_field_pair`, `filter_chip`, `result_card`, `itinerary_summary`, `booking_form`, `primary_button`.
- Prioritize fixing: paired-field alignment, result row scanability, filter proximity, summary/CTA separation, form grouping.
- Risks: treating paired fields as independent cards can break the booking decision model.

## mobile_health_dashboard

- Applicable when: A mobile screen contains health metrics, service cards, doctor rows, appointment rows, activity charts, nutrition logs, or daily summaries.
- Typical nodes: `health_metric_card`, `service_grid`, `doctor_row`, `appointment_row`, `mobile_chart`, `nutrition_row`, `article_card`.
- Prioritize fixing: metric comparability, chart label clearance, service icon-label grouping, list row alignment, data unit readability.
- Risks: dense health data needs stronger readability; do not compress numeric labels to preserve visual impact.

## mobile_social_messaging

- Applicable when: A mobile screen contains chat list, message thread, input bar, comments, social feed, video call grid, rooms, or call history.
- Typical nodes: `chat_row`, `message_bubble`, `message_input`, `comment_row`, `video_tile`, `call_controls`, `feed_card`.
- Prioritize fixing: sender/receiver axis, sticky input clearance, chat row alignment, participant grid stability, comments/action separation.
- Risks: normalizing all bubbles to one width can erase sender/receiver structure and message rhythm.

## mobile_feed_news

- Applicable when: A mobile screen contains featured story, editorial carousel, article card, category rail, author row, date, body text, or related article list.
- Typical nodes: `article_card`, `featured_story`, `category_control`, `carousel`, `author_row`, `body`, `related_list`.
- Prioritize fixing: image/title/date pairing, editorial hierarchy, carousel peek, long-body clearance, category/list attachment.
- Risks: constraining carousels to the viewport can remove intended swipe affordance.

## mobile_settings_account

- Applicable when: A mobile screen contains account/profile header, settings rows, grouped sections, dividers, toggles, chevrons, tab bar, modal panel, or destructive action.
- Typical nodes: `profile_header`, `settings_group`, `settings_row`, `divider`, `toggle`, `tab_bar`, `modal_panel`, `destructive_action`.
- Prioritize fixing: row axis alignment, divider bounds, section header attachment, profile/header separation, destructive-action clarity.
- Risks: making all rows identical can hide danger/destructive state or modal hierarchy.

## comparison

- Applicable when: Two or more alternatives, plans, products, or states must be compared.
- Typical nodes: `title`, `card`, `body`, `chart`, `button`, `caption`.
- Prioritize fixing: column equality, label alignment, shared baselines, consistent card size.
- Risks: equal sizing may hide meaningful asymmetry.

## process_pipeline

- Applicable when: A slide explains a mechanism or system pipeline with sequential stages, intermediate mechanism nodes, side tasks, and a bottom output/takeaway area.
- Typical nodes: `title`, `subtitle`, `process_step`, `connector`, `mechanism_graph`, `task_panel`, `output_group`, `takeaway`.
- Prioritize fixing: left-to-right reading path, connector clutter, region separation, task sidebar grouping, output band stability.
- Risks: reducing connector complexity too aggressively can erase meaningful relationships; preserve all semantic relationships even when rerouting lines.

## layered_system_graph

- Applicable when: A system explanation uses stacked layers such as top graph, middle process flow, bottom graph, right result panel, and legend.
- Typical nodes: `title`, `subtitle`, `region`, `graph_node`, `process_step`, `connector`, `legend`, `sidebar`, `result_panel`.
- Prioritize fixing: title protection, clear horizontal process path, top/bottom region boundaries, connector routing, legend separation.
- Risks: over-normalizing graph nodes can make the graph look decorative instead of causal; keep layer labels and legend meanings intact.
