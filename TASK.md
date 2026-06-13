# TASK.md - Ingestion Execution Contract

**Status:** done
**Goal:** Ingest a raw knowledge item and systematically compile, synthesize, cross-link, and verify it in the LLM Wiki.

## Done When

- [x] Raw input is parsed and decomposed into a plan.
- [x] Planner and Reviewer complete debate loop, scoring $\ge 8$.
- [x] New wiki pages are generated inside the `wiki/` directory with a valid frontmatter schema.
- [x] Internal cross-links are resolved, and `wiki/index.md` is updated.
- [x] The Tester Agent verifies that no broken links or schema violations exist.
- [x] Execution details are successfully logged in `journal.md`.

## Execution Log

- [2026-05-22 20:13] Ingested raw item "Model Context Protocol" successfully. All checks passed.
