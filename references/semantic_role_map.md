# Semantic Role Map

Semantic roles tell Frame Doctor what a node does before deciding where it should move.

## Roles

- `title`: Primary heading for the frame or section.
- `subtitle`: Secondary heading or supporting line.
- `body`: Paragraph or long-form explanatory text.
- `image`: Photo, illustration, screenshot, or other media.
- `chart`: Data visualization, graph, table, or metric display.
- `card`: Repeated content module, KPI tile, feature block, list item, or panel.
- `button`: Primary or secondary action.
- `caption`: Supporting text attached to image, chart, or figure.
- `footer`: Low-priority content at the bottom.
- `navigation`: Header nav, sidebar nav, tabs, bottom nav, breadcrumbs, or filters when acting as navigation.
- `app_shell`: Persistent dashboard/application shell such as left nav, logo, or utility menu.
- `top_bar`: Dashboard header with title, search, profile, alerts, or global actions.
- `kpi_card`: Summary metric card, often in the top row.
- `primary_chart`: Main chart that carries the primary analytic story.
- `secondary_chart`: Supporting chart or breakdown module.
- `filter`: Filter, search, date range, segment control, or dashboard control.
- `table`: Tabular or row-based data region.
- `status_panel`: Operational status module, server status, system health, or problem summary.
- `activity_feed`: Recent activity, event list, or update feed.
- `timeline`: Vertical or horizontal event timeline.
- `review_card`: Lower-priority repeated review/comment/task record card.
- `status_bar`: Mobile top system bar or reserved top safe area.
- `home_indicator`: Mobile bottom system indicator or reserved bottom safe area.
- `safe_area`: Mobile region that content should not enter.
- `hero_media`: Onboarding image, illustration, carousel image, or dominant visual field.
- `title_block`: Grouped mobile title, subtitle, and nearby onboarding message.
- `pagination`: Dots, line paginator, progress bar, or carousel position indicator.
- `primary_button`: Main CTA.
- `secondary_button`: Secondary CTA, skip, sign up, or lighter action.
- `bottom_action`: Bottom CTA group, bottom nav, or next/skip control zone.
- `form_group`: Group of mobile form fields, helper text, and form-specific controls.
- `form_field`: Text input, select input, verification field, or form row.
- `field_label`: Label attached to a form field.
- `helper_text`: Field helper, legal note, error note, or password recovery text.
- `social_login`: Third-party login button or group of social login options.
- `bottom_sheet`: Modal sheet anchored to the bottom of a mobile screen.
- `profile_header`: Avatar, name, handle, bio, and primary profile identity group.
- `avatar`: User profile image or identity marker.
- `stats_row`: Comparable social/profile metrics row.
- `profile_action`: Follow, message, edit profile, or other profile-scoped action.
- `gallery_grid`: Mobile media grid, photo grid, product grid, or profile gallery.
- `media_tile`: Single tile inside a gallery or media grid.
- `bio`: Profile bio, about text, or personal description.
- `list_item`: Generic mobile list row when a more specific row role is unavailable.
- `media_artwork`: Dominant album, video, photo, or media thumbnail.
- `media_metadata`: Track, artist, album, duration, or media description group.
- `progress_line`: Media progress, carousel progress, playback scrubber, or timeline control.
- `media_controls`: Playback, capture, edit, crop, or media action control cluster.
- `lyrics`: Lyric, transcript, caption, or long media text region.
- `queue_row`: Playlist, queue, album item, or media list row.
- `product_card`: Product image, title, price, rating, badge, and action unit.
- `product_image`: Product-specific media region.
- `price`: Price, discount, subtotal, or total value.
- `rating`: Rating stars, review count, or reputation indicator.
- `variant_selector`: Product option selector such as size, color, quantity, or filter value.
- `cart_item`: Cart row with product, quantity, price, and removal action.
- `checkout_summary`: Order summary, subtotal, delivery, tax, or total group.
- `filter_sheet`: Filter panel, sort sheet, or faceted controls panel.
- `search_field`: Mobile search, location, date, or query input.
- `booking_field_pair`: Paired booking inputs such as origin/destination or start/end date.
- `filter_chip`: Filter tag, category chip, or selected option pill.
- `result_card`: Search result, travel result, doctor result, or listing card.
- `itinerary_summary`: Trip, booking, appointment, or schedule summary group.
- `booking_form`: Passenger, contact, payment, or reservation form group.
- `health_metric_card`: Health, fitness, nutrition, or activity metric card.
- `service_grid`: Mobile grid of services, shortcuts, categories, or feature icons.
- `doctor_row`: Doctor, provider, specialist, or appointment person row.
- `appointment_row`: Appointment, schedule, reminder, or booking row.
- `mobile_chart`: Mobile chart, progress ring, bar chart, trend card, or numeric plot.
- `nutrition_row`: Food, ingredient, meal, calorie, or nutrition list row.
- `chat_row`: Conversation list row with avatar, title, preview, time, and unread state.
- `message_bubble`: Sent or received chat bubble.
- `message_input`: Sticky composer/input bar in a chat or comment screen.
- `comment_row`: Comment, reply, review, or discussion row.
- `video_tile`: Video call participant tile or media participant panel.
- `call_controls`: Voice/video call control cluster.
- `feed_card`: Social feed or post card.
- `article_card`: Editorial article card with image, label, title, date, or source.
- `featured_story`: Lead editorial story or hero article.
- `category_control`: Category rail, segment control, or editorial filter row.
- `carousel`: Horizontal carousel, pager, or side-peeking card rail.
- `author_row`: Author/source row, date row, byline, or follow action row.
- `related_list`: Related articles, recommendations, or secondary editorial list.
- `settings_group`: Group of settings rows under one section.
- `settings_row`: Settings item row with icon, label, value, toggle, or chevron.
- `divider`: Row divider or section separator.
- `toggle`: Switch, checkbox, radio, or binary control.
- `tab_bar`: Bottom tab bar or persistent mobile navigation bar.
- `modal_panel`: Modal, side panel, centered panel, or overlay surface.
- `destructive_action`: Logout, delete, cancel subscription, or other destructive setting.
- `process_step`: A numbered or ordered stage in a workflow or pipeline.
- `connector`: Line, arrow, curve, dashed path, or loop that explains relationships between nodes.
- `mechanism_graph`: A state graph, radial graph, causal graph, or other mechanism diagram.
- `graph_node`: A node inside a graph or state model.
- `task_panel`: Panel containing main/sub task instructions, checks, or actions.
- `result_panel`: Panel containing outcomes, metrics, or training result summaries.
- `output_group`: Bottom or terminal collection of resulting metrics, chips, or output modules.
- `region`: Container that separates a semantic layer or major system area.
- `legend`: Explanation of colors, line types, symbols, or graph encodings.
- `takeaway`: Final summary bar, claim, or conclusion.
- `unknown`: Missing or ambiguous role.

## Confidence Rules

An LLM may propose a tentative role from node id, type, text, position, and nearby nodes. It must not silently lock a low-confidence role when that role affects layout. Mark the role as `unknown` or ask the user.

## Role Mapping Output

Represent role mapping as:

```json
{
  "node_id": "body_01",
  "role": "body",
  "confidence": 0.84,
  "evidence": ["explicit role field", "text node", "long copy"]
}
```
