# GEMINI.md - Gemini CLI & API Operational Guidelines

This file governs the behaviors of Google's **Gemini CLI** and **Google Generative AI** agents operating within this repository.

---

## 1. Model Selection & Routing

- **Routing Model (`gemini-2.5-flash-lite`):** Use for quick validations, keyword queries, list-checks, and lightweight text parsing. Very fast and cost-effective.
- **Reasoning Model (`gemini-2.5-flash` or `gemini-2.5-pro`):** Use for deep Planner-Reviewer debate loops, synthesizing complex markdown articles, resolving conflicting text pages, and schema migrations.

---

## 2. API Format & Constraints

- **Mandatory JSON Output:** When calling tools, ensure command structures specify `--output-format json` to facilitate python-based parsing inside `orchestrator.py`.
- **Command CLI format:** Standard oneshot CLI executions require passing the prompt using the `-p` argument (`gemini.cmd -p "<prompt>"`).
- **Session Control:** Ensure that the local session state database remains active. When continuing a multi-agent debate loop, reuse the established `session_id` using `--resume <session-id>` to prevent lost context.

---

## 3. Operations Guardrails

- **Explicit Schema Validation:** Always output frontmatter strictly wrapped in double-dashes `---` to prevent structural parsing crashes.
- **Relative Linking:** Validate that all internal page URLs are formatted exactly as relative Markdown paths (e.g., `(/wiki/name.md)`), avoiding standard web URLs.
- **Safety sandboxing:** Always ensure command execution limits remain bound to `llm_wiki_repository/`. Do not execute commands outside the workspace root.
