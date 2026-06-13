# Scheme Operation Plan: LLM Wiki Database Specs

This document defines the strict scheme and metadata management standards governing the **LLM Wiki**. To maintain programmatic queryability and syntactic alignment across multi-agent executions, every page MUST conform to these specifications.

---

## 1. Metadata Schema Definition

All wiki files (residing in the `wiki/` directory) must encapsulate a YAML Frontmatter block.

### 1.1 Structural Specification

```yaml
---
title: "Standard Entity Name"
tags: ["domain", "subdomain", "technology"]
last_updated: YYYY-MM-DD
links: ["/wiki/relative_page.md"]
version: 1.0
---
```

### 1.2 Mandatory Field Validations

1. **`title` (String):** Must be surrounded by double quotes. Must match the principal `<h1>` header of the markdown body.
2. **`tags` (Array of Strings):** Must be lowercase alphanumeric strings. Max 5 tags per document to prevent index noise.
3. **`last_updated` (Date):** Formatted as `YYYY-MM-DD` representation of the last transaction update.
4. **`links` (Array of Strings):** List of root-relative targets. E.g., `"/wiki/agentic_coding_basics.md"`.
5. **`version` (Float):** Starts at `1.0`. Incremented by `0.1` upon minor updates, and by `1.0` upon complete file restructurings.

---

## 2. Linking & Reference Integrity

To prevent a highly fragmented graph, the wiki enforces strict **Link Routing Standards**:

- **No Absolute Paths:** Paths such as `C:\Users\...\wiki\index.md` are banned. Only root-relative paths like `/wiki/index.md` are valid.
- **Bidirectional Links:** If `page_a.md` creates a reference to `page_b.md`, `page_b.md` must register a reciprocal reference to `page_a.md` in its frontmatter `links` array or markdown content.
- **Index Entry Point:** Every new page created must be indexed by the main homepage index `wiki/index.md`. Orphaned pages (pages with 0 incoming links) are flagged as maintenance alerts.

---

## 3. Schema Evolution & Migration Procedure

If a schema field is added, modified, or removed, the Orchestrator executes a structured **Schema Migration Ingestion**:

1. **Planner Formulation:** The Planner outlines the migration rule (e.g., adding `author` field to all pages).
2. **Harness Audit:** A temporary `Migration_TODO.md` is registered in `specs/`.
3. **Coder Automation:** The Coder scans the entire `wiki/` folder, parses the YAML block of each file, inserts the default value of the new field, and increments the `version` key.
4. **Tester Audit:** The Tester validates that every page parses correctly under the new schema rules.
5. **Journal Verification:** The migration run is successfully appended to `journal.md`.
