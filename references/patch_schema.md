# Patch Schema

Frame Doctor patches are JSON objects that describe reversible layout operations.

## Top-level Shape

```json
{
  "version": "1.0",
  "patch_id": "patch_two_column_001",
  "pattern": "two_column",
  "rationale": "Separate body and image into columns to remove overlap.",
  "operations": []
}
```

## Supported Operations

### move_resize

```json
{
  "op": "move_resize",
  "node_id": "body",
  "x": 96,
  "y": 200,
  "width": 760,
  "height": 620
}
```

### group

```json
{
  "op": "group",
  "group_id": "group_hero_media",
  "node_ids": ["image", "caption"],
  "metadata": {"role": "figure"}
}
```

### ungroup

```json
{"op": "ungroup", "group_id": "group_hero_media"}
```

### apply_auto_layout

```json
{
  "op": "apply_auto_layout",
  "target_id": "kpi_group",
  "direction": "horizontal",
  "spacing": 32,
  "padding": 0
}
```

### set_constraints

```json
{
  "op": "set_constraints",
  "node_id": "bottom_nav",
  "horizontal": "stretch",
  "vertical": "bottom"
}
```

### normalize_spacing

```json
{
  "op": "normalize_spacing",
  "node_ids": ["card_1", "card_2", "card_3"],
  "axis": "x",
  "spacing": 24
}
```

### align_edges

```json
{
  "op": "align_edges",
  "node_ids": ["card_1", "card_2", "card_3"],
  "edge": "top"
}
```

### resize_text_box

```json
{
  "op": "resize_text_box",
  "node_id": "body",
  "width": 760,
  "height": 560
}
```

### snap_to_grid

```json
{
  "op": "snap_to_grid",
  "node_ids": ["title", "body", "image"],
  "grid_size": 8
}
```

### pair_caption_image

```json
{
  "op": "pair_caption_image",
  "image_id": "image",
  "caption_id": "caption",
  "gap": 24,
  "align": "left"
}
```

### define_region

```json
{
  "op": "define_region",
  "region_id": "top_global_graph",
  "role": "mechanism_graph_layer",
  "node_ids": ["global_graph_title", "global_graph_nodes"],
  "x": 64,
  "y": 156,
  "width": 1460,
  "height": 286
}
```

### route_connectors

```json
{
  "op": "route_connectors",
  "connector_ids": ["line_top_update", "line_bottom_update"],
  "style": "orthogonal",
  "avoid_node_ids": ["step_01", "step_02", "step_03"],
  "metadata": {"green": "upper graph update", "blue": "lower graph update"}
}
```

## Forbidden Operations

Patch producers must not emit:

- `delete_content`
- `rewrite_text`
- `replace_image`
- `change_brand_style`
- `flatten_editable_layers`

Patch appliers should reject unknown destructive operations rather than trying to interpret them.
