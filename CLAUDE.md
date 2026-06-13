# CLAUDE.md - Claude Code Operational Guidelines

This file governs the behaviors of Anthropic's **Claude Code** and **Claude CLI** agents operating within this repository. 

---

## 1. System Commands & Automation

To verify changes, execute the following commands in the workspace root:

- **Build / Verification:** `python pipeline.py maintain`
- **Quality Assurance Audit:** `python orchestrator.py`
- **Linting:** Ensure clean, valid Markdown formatting (GFM). Ensure YAML frontmatter is present and valid.

---

## 2. Operational Style & Safeguards

- **Explore Before Coding:** Before modifying any file inside the `wiki/` directory, you must run `list_dir` or `read_file` to thoroughly map the surrounding cross-references and tags.
- **Strict Relative Routing:** Never write absolute local file paths or web-absolute paths for internal links. Only use root-relative Markdown references (e.g. `[Page Name](/wiki/page_name.md)`).
- **Atomic Commits:** Make small, incremental modifications. Do not perform sweeping refactorings in a single turn.
- **No Test Skips:** If the Tester Agent flags a broken link or malformed frontmatter, you must fix it immediately. Never ignore, bypass, or mock out a validation failure.
- **Stop and Report:** If you fail to resolve a broken path or schema check after 3 consecutive attempts, write the error details to `journal.md` and exit to ask the user.
