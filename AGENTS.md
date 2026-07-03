# Frame Doctor Agent Instructions

Use Frame Doctor before final output whenever you generate or modify layout geometry for canvas JSON, PPT-like structure, Figma-like frames, dashboards, mobile screens, or infographics.

Do not return unaudited layout geometry. If a canvas has `overlap`, `out_of_bounds`, `text_overflow`, `margin_breach`, `image_caption_detachment`, or `hierarchy_ambiguity`, run repair or report the remaining conflicts.

Always preserve text, images, brand style, semantic relationships, and editability. Do not delete content, rewrite copy, replace assets, flatten layers, or silently change the visual identity.

Prefer the stable Skill CLI over low-level scripts:

```bash
python scripts/frame_doctor_skill.py repair canvas.json --profile readability_first --output repaired.json
```

For generation tasks, first request constraints:

```bash
python scripts/frame_doctor_skill.py generation-brief --target ppt --profile readability_first
```

For final checking, guard the output:

```bash
python scripts/frame_doctor_skill.py guard canvas.json --profile readability_first --fail-on-critical
```

Use the LDS five-step flow:

1. L0 detect facts.
2. L1 propose structure.
3. L2 apply human value profile.
4. L3 emit or apply patch.
5. L4 audit before final answer.
