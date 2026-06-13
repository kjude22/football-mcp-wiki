# Operational Harness Rules

These rules govern the autonomous execution of the LLM Agent inside this repository.

---

## 1. Directory Structure Constraints
*   All source documents must be loaded from `raw/`.
*   All compiled markdown articles must be saved to `wiki/` using lowercase snake_case naming conventions (e.g., `cristiano_ronaldo.md`).
*   The system schema definition is maintained in `schema/schema.md`.

---

## 2. Ingestion & Compilation Pipeline
1.  **Read Raw Input:** Read the text file from `raw/`.
2.  **Generate Markdown with YAML:** Convert it into a clean Markdown file with double-quoted titles, lowercase tags, and cross-links in the YAML frontmatter.
3.  **Cross-linking:** Ensure bidirectional cross-linking. If page A links to page B, page B must list page A in its `links` frontmatter field.
4.  **Audit Syntax:** Run the validation script `harness/skills/audit_syntax.py` before finalizing any changes.

---

## 3. Security Sandbox Policy
*   Do NOT modify any python source files in `tools/` or HTML/JS/CSS assets in `gui/`.
*   Do NOT invoke external APIs or execute raw shell commands. Only communicate through standard input/output with the FastMCP tools.
