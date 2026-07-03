# Frame Doctor 3-Minute Competition Demo

This script shows Frame Doctor as LDS: Layout Decision System. The goal is to prove that the system does not silently beautify a layout. It detects facts, asks for value decisions, applies constraints, and audits the result.

## 0:00-0:30 - Show Before

Open or show the broken case:

```bash
python3 scripts/render_canvas_html.py assets/demo_cases/case_01_ppt_content_before.json --output case_01_before.html
```

Point out the visible problems:

- Body and image overlap.
- Image and caption overlap.
- Reading order is unclear.

## 0:30-0:55 - Run Diagnose

Run objective conflict detection:

```bash
python3 scripts/frame_doctor_skill.py diagnose assets/demo_cases/case_01_ppt_content_before.json
```

Narration:

- L0 detects facts before any aesthetic decision.
- Critical conflicts are machine-verifiable.
- The system does not yet decide the final design direction.

## 0:55-1:45 - Enter Interactive Gate

Start the human-in-the-loop competition mode:

```bash
python3 scripts/run_demo.py assets/demo_cases/case_01_ppt_content_before.json --profile assets/value_profiles/readability_first.json --interactive
```

Walk through the gates:

1. Fact Gate: confirm the canvas and conflict count.
2. Meaning Gate: confirm semantic roles.
3. Value Gate: choose or confirm `readability_first`.
4. Constraint Gate: review the proposed patch operations.
5. Commit Gate: accept only after audit metrics are visible.

Narration:

- Structure and value decisions remain reviewable by the human.
- Readability is chosen because this is a PPT explanation slide.

## 1:45-2:25 - Apply Repair

For a fast repeatable run, use batch automatic profile mode:

```bash
python3 scripts/run_demo.py assets/demo_cases/case_01_ppt_content_before.json --profile assets/value_profiles/readability_first.json --output-json repaired_case_01.json --visual-output case_01_before_after.html
```

Expected headline metrics:

- Score: `60 -> 100`
- Critical conflicts: `2 -> 0`
- Overlap area: `121120.0 -> 0.0`

## 2:25-3:00 - Show After and Audit

Open `case_01_before_after.html` and show the side-by-side comparison.

Then guard the repaired output:

```bash
python3 scripts/frame_doctor_skill.py guard repaired_case_01.json --profile readability_first --fail-on-critical
```

Close with:

- Frame Doctor is not a generic layout assistant.
- It is an executable decision loop for layout repair.
- The main competition scope is `process_pipeline`, `layered_system_graph`, and `dashboard` / `card_grid`.
