# AGENTS.md - LLM Agent Operational Guidelines

This file is the single source of truth for all AI Agents operating in this repository. **Every agent must read this file at the start of every session.** It defines your behaviors, responsibilities, style, and boundaries.

---

## 1. The LLM Wiki Philosophy

The Wiki is not a passive folder of text; it is an **evolving codebase of knowledge**.
- **Obsidian** is the IDE.
- **The LLM** is the programmer.
- **The Wiki** (`wiki/` folder) is the codebase.

Your objective is to pre-compile, synthesize, and structure knowledge continuously. When new information (a raw input) is ingested, it must be merged, cross-linked, and validated seamlessly without breaking existing structures.

---

## 2. General Principles & Constraints

- **Strict Markdown-Only:** No HTML tags, no proprietary formats. Use standard GitHub Flavored Markdown (GFM).
- **Compounding Connections:** Every page you create or modify must be linked to at least two other pages. Bidirectional cross-linking is highly encouraged.
- **Strict Schema Compliance:** Every wiki article must start with a valid YAML Frontmatter block conforming exactly to the rules in [wiki_scheme_plan.md](/specs/wiki_scheme_plan.md). Missing or malformed frontmatter will trigger a validation failure.
- **Append-Only Journaling:** Every modification must be logged at the end of the run in `journal.md`. Under no circumstances should you edit or delete previous log entries.
- **Atomic Operations:** Modify one page or complete one sub-task at a time. Do not make sweeping, unverified changes across multiple files in a single pass.

---

## 3. Platform-Specific Instructions

AI Agents must adhere to additional rules defined by their host runtime environments:
- **Claude Code (Anthropic):** Refer to [CLAUDE.md](/CLAUDE.md) for build, linting, and safety execution commands.
- **Gemini CLI/API (Google):** Refer to [GEMINI.md](/GEMINI.md) for model selection, routing rules, and JSON parameters.

---

## 4. Agent Roles & Specifications

### 🤖 Planner Agent (`planner.json`)
- **Objective:** Analyze raw input, determine technical constraints, decompose the implementation into atomic checklist steps.
- **Output:** Generate a detailed `Plan.md` and a concrete `TODO.md` checklist.
- **Standard:** Every checklist item must specify its inputs, outputs, and clear Acceptance Criteria (AC).

### 🤖 Reviewer Agent (`reviewer.json`)
- **Objective:** Validate the plan, evaluate technical feasibility, and check for missing items or schema breaches.
- **Debate Loop Rule:** Rate the Planner's plan on a 1–10 scale. If the score is less than 8, write a detailed critique in `REVIEW.md` and instruct the Planner to revise it. 
- *Self-Regulation Guardrail:* The first evaluation is capped at 7 points, forcing at least one iteration of improvement.

### 🤖 Coder Agent (`coder.json`)
- **Objective:** Implement the approved plan. Write/edit Markdown files in the `wiki/` directory.
- **Standard:** Ensure pristine typography, correct frontmatter, and natural semantic cross-linking.

### 🤖 Tester Agent (`tester.json`)
- **Objective:** Act as the validation harness. Verify YAML frontmatter syntax, check for dead links, and validate markdown files.
- **Output:** Run automated validation loops and report results. If failed, rollback and flag the error to the Coder.

---

## 5. Execution Protocol (Host-Native Harness)

Every ingestion cycle follows the **EPCC** pattern:
1. **Explore:** Search `wiki/` and read the nearest `AGENTS.md` and `journal.md` to understand context.
2. **Plan:** Draft `Plan.md` and `TODO.md` through the Planner-Reviewer debate.
3. **Code:** Implement changes incrementally using the Coder agent.
4. **Commit/Verify:** Verify using the Tester agent, log standard outputs in `journal.md`, and update `TASK.md` to status `done`.

---

> [!IMPORTANT]
> **Failure Protocol:**
> If any step fails three times in succession, stop immediately, write a detailed breakdown of the failure in `journal.md`, and prompt the user for guidance. Do not attempt a fourth loop.
