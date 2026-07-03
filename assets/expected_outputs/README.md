# Expected Outputs

Demo output is written to stdout as a Markdown report. A successful MVP run should show:

- A lower `error_count` after repair than before repair.
- A `recommended_patch` with concrete operations.
- A `Layout QA Report` that includes before and after scores.

The exact operation coordinates can change as the rule engine evolves, but patches must preserve content and avoid forbidden operations.
