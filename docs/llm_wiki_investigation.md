# Investigation Report: The LLM Wiki Paradigm

## 1. Executive Summary

In April 2026, AI researcher Andrej Karpathy introduced the **LLM Wiki** paradigm, describing a personal knowledge management pattern where a local folder of plain Markdown files functions as an evolving codebase, an editor (like Obsidian) serves as the IDE, and an autonomous LLM acts as the programmer. 

This report investigates the architecture of the LLM Wiki, evaluates its operational benefits over traditional RAG (Retrieval-Augmented Generation), outlines the role of autonomous agent pools, and establishes a schema operational plan for automated maintenance.

---

## 2. RAG vs. LLM Wiki: The Pre-Compilation Paradigm

Traditional knowledge systems rely heavily on vector databases and runtime search queries to retrieve and synthesize information. The following table contrasts standard RAG with the pre-compiled LLM Wiki approach.

| Architectural Dimension | Traditional Vector-RAG | Pre-compiled LLM Wiki |
| :--- | :--- | :--- |
| **Data Lifecycle** | Transient; raw documents are parsed, chunked, and embedded dynamically per query. | Persistent; knowledge is structured, merged, and cross-linked inside a markdown folder. |
| **Compilation Cost** | Low upfront, high runtime. Every user query initiates vector searches and context injection. | High upfront, near-zero runtime. LLM preprocesses and synthesizes pages before query time. |
| **Semantic Coherence** | Low; retrieves isolated text chunks. Often loses holistic context or structural relationships. | High; pages represent complete entities with relative links mapping semantic connections. |
| **Technical Debt** | High; duplicated or contradictory chunks in raw documents lead to halluncinated or competing context. | Low; agents continuously audit the directory to resolve contradictions and clean up files. |
| **Human Readability** | Low; raw chunks stored in proprietary vector stores (Pinecone, Chroma, SQLite). | High; plain GitHub Flavored Markdown (GFM) readable by both humans and AI models. |

### The "Pre-Compilation" Metaphor
In standard RAG, the LLM is treated as an *interpreter* that compiles raw code (raw documents) at runtime on every single request. 
In the LLM Wiki, the LLM is treated as a *compiler*. When new knowledge (raw input) is introduced, the compiler parses it, merges it into the existing AST (the wiki folder), optimizes connections (cross-references), and outputs a statically verified, high-performance representation (clean, linked Markdown) that can be read instantaneously by both humans and LLM models.

---

## 3. Core Architectural Components

An LLM Wiki comprises three interconnected layers:

```
┌────────────────────────────────────────────────────────┐
│                   Harness & Policy                     │
│         (specs/schema.md, AGENTS.md, TASK.md)          │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Agent Pool Layer                     │
│          (Planner ──► Reviewer ──► Coder)              │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Semantic Codebase                      │
│                  (wiki/ *.md files)                    │
└────────────────────────────────────────────────────────┘
```

1. **The Semantic Codebase (`wiki/`):** A collection of highly curated, modular Markdown files utilizing strict metadata headers (YAML frontmatter) and relative linking conventions.
2. **The Agent Pool Layer:** Specialized, autonomous subprocesses coordinating tasks. Rather than a single conversation generating a generic file, a pipeline of Planner, Reviewer, and Coder agents debate and implement changes.
3. **Harness & Policy Layer:** Root-level operational bounds (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) and contract sheets (`TASK.md`) that constrain the agents, preventing hallucinated file writes, loops, or historical revisionism.

---

## 4. User Query & Maintenance Mechanics

### 4.1 The User Query Flow
When a user queries the wiki:
1. The query processor uses lightweight lexical or semantic keyword parsing to locate relevant nodes inside the wiki folder.
2. The orchestrator maps out the neighboring files by reading the `links` metadata array in the page's YAML frontmatter.
3. Relevant markdown files are loaded in full into the context window of a reasoning model.
4. The model synthesizes the pre-organized knowledge, producing a highly cohesive response complete with page references, avoiding fragmented context-chunking.

### 4.2 The Maintenance Audit
Like any code base, an LLM Wiki faces **entropy**. To prevent deterioration, automated maintenance routines execute scheduled or transactional audits:
- **Orphan Detection:** Locating pages that have 0 incoming links from other wiki files.
- **Dead Link Scanning:** Verifying that all relative link references point to files that actually exist in the folder.
- **Frontmatter Validation:** Checking that all YAML headers are syntactically valid and contain mandatory fields (`title`, `tags`, `last_updated`, `links`, `version`).
- **Index Compilation:** Automatically rebuilding the central navigation index (`wiki/index.md`) to reflect newly added or deleted nodes.
