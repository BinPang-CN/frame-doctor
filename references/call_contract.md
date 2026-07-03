# Frame Doctor Skill Call Contract

Frame Doctor exposes a stable command-line interface for Codex, LearnBuddy, and other agents through `scripts/frame_doctor_skill.py`.

## Input Canvas Schema

A canvas JSON should contain:

```json
{
  "frame": {
    "id": "slide_01",
    "width": 1920,
    "height": 1080,
    "safe_margin": 96
  },
  "layout_metadata": {
    "grid_size": 8,
    "baseline_grid": { "interval": 8 }
  },
  "nodes": [
    {
      "id": "title",
      "role": "title",
      "type": "text",
      "x": 96,
      "y": 80,
      "width": 1000,
      "height": 72,
      "text": "Launch readiness"
    }
  ]
}
```

Required node geometry fields are `id`, `x`, `y`, `width`, and `height`. Recommended semantic fields are `role`, `type`, and `text` for text nodes.

## Output Patch Schema

`propose` returns the same proposal object as `scripts/propose_layout_patch.py`, including:

```json
{
  "recommended_patch": {
    "version": "1.0",
    "patch_id": "patch_two_column_001",
    "pattern": "two_column",
    "operations": [
      {
        "op": "move_resize",
        "node_id": "title",
        "x": 96,
        "y": 96,
        "width": 1728,
        "height": 82
      }
    ]
  }
}
```

Patch operations must preserve content, images, brand style, semantic relationships, and editability.

## CLI Commands

```bash
python scripts/frame_doctor_skill.py diagnose canvas.json
python scripts/frame_doctor_skill.py propose canvas.json --profile readability_first
python scripts/frame_doctor_skill.py repair canvas.json --profile readability_first --output repaired.json --visual-output comparison.html
python scripts/frame_doctor_skill.py guard canvas.json --profile readability_first --fail-on-critical
python scripts/frame_doctor_skill.py generation-brief --target ppt --profile readability_first
```

`--profile` accepts either a name from `assets/value_profiles/` such as `readability_first` or a direct JSON file path.

## Exit Code Behavior

- `diagnose`, `propose`, `repair`, and `generation-brief` return `0` on success.
- `guard` returns `0` unless `--fail-on-critical` is set and critical conflicts remain.
- Any command returns `2` for invalid input, unknown profile, or unexpected execution errors.

## Generation-Time Usage

Before creating geometry, call:

```bash
python scripts/frame_doctor_skill.py generation-brief --target ppt --profile readability_first
```

Use the returned safe margin, gutter, grid strategy, preservation rules, and forbidden errors while drafting the layout.

## Post-Generation Usage

Before final delivery, call:

```bash
python scripts/frame_doctor_skill.py guard draft_canvas.json --profile readability_first --fail-on-critical
```

If guard fails, call:

```bash
python scripts/frame_doctor_skill.py repair draft_canvas.json --profile readability_first --output repaired.json --visual-output comparison.html
```

Return the repaired canvas, audit summary, and visual HTML when available.

## Example Agent Workflow

1. Agent receives request: "generate a PPT slide about launch readiness".
2. Agent calls `generation-brief`.
3. Agent generates draft canvas JSON using the returned constraints.
4. Agent calls `guard`.
5. If guard fails, agent calls `repair`.
6. Agent returns repaired canvas, audit summary, and visual HTML.
