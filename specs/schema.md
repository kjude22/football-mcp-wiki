# Wiki Metadata & Formatting Schema Specification

To ensure machine readability, interoperability, and semantic integrity, all pages in the **LLM Wiki** must strictly adhere to the following schema.

---

## 1. YAML Frontmatter Schema

Every markdown file (except for index tables or control documents) MUST start with a YAML Frontmatter block wrapped in triple dashes (`---`).

### Required Fields

| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `title` | String | A concise, human-readable page title | `"Model Context Protocol"` |
| `tags` | Array | Relevant categories in lowercase alphanumeric format | `["mcp", "api", "protocol"]` |
| `last_updated` | Date | Timestamp of the last successful merge (YYYY-MM-DD) | `2026-05-22` |
| `links` | Array | List of relative file paths that this page links to | `["/wiki/index.md", "/wiki/agent.md"]` |
| `version` | Float | Page version, incremented by 0.1 on each revision | `1.1` |

### Sample Block

```yaml
---
title: "Agentic Coding Basics"
tags: ["ai", "software-engineering", "agents", "sdlc"]
last_updated: 2026-05-22
links: ["/wiki/index.md", "/wiki/model_context_protocol.md"]
version: 1.0
---
```

---

## 2. Formatting Guidelines

### 2.1 File Naming
- File names must be lowercase, using underscores instead of spaces or hyphens.
- Example: `model_context_protocol.md` instead of `Model-Context-Protocol.MD`.
- Every page must reside inside the `wiki/` directory.

### 2.2 Heading Structure
- A single `<h1>` (`#`) tag must be used at the top of the file, matching the frontmatter `title`.
- Use logical hierarchies for sections (`##`, `###`, etc.).

### 2.3 Cross-linking Rules
- Links must use standard Markdown syntax: `[Link Text](/wiki/filename.md)`.
- **CRITICAL:** Do NOT use absolute system paths (e.g. `C:/Users/.../wiki/filename.md`). Only relative root-based paths (`/wiki/filename.md`) are permitted.
- Broken links are considered build failures and will be rejected by the Tester Agent.

### 2.4 Code Blocks
- Use fenced code blocks with appropriate language tags (e.g. `python`, `json`, `markdown`, `yaml`) for syntax highlighting.
