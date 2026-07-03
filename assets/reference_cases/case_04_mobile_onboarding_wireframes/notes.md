# Case 04 - Mobile Onboarding Wireframes Reference

## Source

- Figma file: `https://www.figma.com/design/Y1xu9CDZebBK8SPvcIJZ07/120%E9%A1%B5%E8%B6%85%E5%85%A8%E7%A7%BB%E5%8A%A8%E7%AB%AF%E8%AE%BE%E8%AE%A1app%E7%BA%BF%E6%A1%86%E5%9B%BE?node-id=22-867`
- Reference node: `22:867` / `Onboarding`
- Local reference image: `figma_reference.png`

## Page Type

Mobile onboarding and sign-in wireframe set.

The inspected node contains multiple 375x812 mobile frames with status bar, home indicator, hero images, title/subtitle blocks, pagination indicators, primary CTA buttons, skip/next controls, bottom sheets, and sign-in action stacks.

## Intended Reading Path

1. Respect system status area first.
2. Read hero or visual state when present.
3. Read title and subtitle as a single grouped message.
4. Use paginator or progress line to understand onboarding position.
5. Read and tap the primary action.
6. Use secondary action only after the primary action is visually understood.
7. Avoid bottom home indicator collision.

## Transferable Layout Pattern

Use `mobile_screen` for general mobile UI repair and `mobile_onboarding` when a screen contains hero media, title block, paginator, and CTA.

Suggested regions:

- `system_top`: status bar.
- `hero_media`: image, carousel, color field, or bottom-sheet backdrop.
- `title_block`: headline, supporting copy, and nearby indicator.
- `bottom_action_area`: primary button, skip, next, secondary action.
- `system_bottom`: home indicator.

## Useful Repair Lessons

- Mobile screens are narrow; text boxes should use stable readable widths rather than full-frame sprawl.
- CTA buttons should sit above the home indicator and preserve touch clearance.
- Paginators should be attached to the onboarding state, either above title, below title, or near carousel context.
- Secondary actions such as `Skip` should be lighter than the primary CTA and placed predictably.
- Hero images can dominate the upper half, but must not squeeze the title/CTA into unsafe areas.
- Side-peeking carousel imagery is intentional; do not center everything if the peek communicates swipe.
- Bottom sheets need large radius and a clear boundary from the backdrop.

## Typical Before Problems This Reference Helps Repair

- CTA or bottom nav extends into the home indicator.
- Title, subtitle, and paginator are separated too far to read as one message.
- Hero image overlaps title or CTA area.
- Primary and secondary buttons have unclear priority.
- Progress line or paginator floats without connection to the onboarding state.
- Carousel images lose edge-peek affordance.
- Stacked buttons have inconsistent width or vertical spacing.

## Recommended Value Profile

```json
{
  "readability": 0.9,
  "visual_impact": 0.6,
  "content_preservation": 0.95,
  "grid_strictness": 0.85,
  "editability": 0.9,
  "touch_safety": 0.95,
  "only_fix_hard_errors": 0.0
}
```

## Suggested Patch Operations

- Use `define_region` for `system_top`, `hero_media`, `title_block`, `bottom_action_area`, and `system_bottom`.
- Use `move_resize` to re-stack hero, title, paginator, and CTA.
- Use `group` for title/subtitle/paginator.
- Use `set_constraints` for bottom action groups pinned above the home indicator.
- Use `apply_auto_layout` metadata for stacked sign-in/sign-up buttons.
