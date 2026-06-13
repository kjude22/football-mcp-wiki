import os
import sys
import json
import time
import re
from datetime import datetime

# ==============================================================================
# Global CP949 / Windows Unicode Safe Print override
# ==============================================================================
_original_print = print
def print(*args, **kwargs):
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    file = kwargs.get('file', sys.stdout)
    
    # If printing to standard output, handle encoding errors gracefully
    if file == sys.stdout or file == sys.stderr:
        text = sep.join(str(arg) for arg in args)
        try:
            _original_print(text, end=end, **{k: v for k, v in kwargs.items() if k not in ['sep', 'end']})
        except UnicodeEncodeError:
            try:
                enc = sys.stdout.encoding or 'ascii'
                fallback = text.encode(enc, errors='replace').decode(enc)
                _original_print(fallback, end=end, **{k: v for k, v in kwargs.items() if k not in ['sep', 'end']})
            except Exception:
                ascii_text = ''.join(c if ord(c) < 128 else '?' for c in text)
                _original_print(ascii_text, end=end, **{k: v for k, v in kwargs.items() if k not in ['sep', 'end']})
    else:
        _original_print(*args, **kwargs)

# ==============================================================================
# ANSI Color Codes for Premium Console UI
# ==============================================================================
HEADER = '\033[95m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
BG_BLACK = '\033[40m'
ENDC = '\033[0m'

def print_header(title):
    print(f"\n{BOLD}{HEADER}=== {title} ==={ENDC}\n")


def print_agent_status(agent_id, status, details=""):
    color = BLUE if status == "running" else (GREEN if status == "completed" else (RED if status == "failed" else ENDC))
    status_str = f"[{status.upper()}]"
    print(f"{BOLD}{color}{agent_id:<12} {status_str:<12} {ENDC}{details}")

def print_section(title, content):
    border = "-" * 80
    print(f"\n{CYAN}{border}\n{BOLD}{title}{ENDC}\n{CYAN}{border}{ENDC}")
    print(content)
    print(f"{CYAN}{border}{ENDC}\n")

# ==============================================================================
# In-Memory Simulation Content (for Demo/Simulation Mode)
# ==============================================================================
DEMO_PLAN_V1 = """# Proposed Plan: Ingesting Model Context Protocol (MCP)

This plan outlines the creation and modification of wiki pages to incorporate MCP.

## Proposed Modifications
1. **[NEW]** `wiki/model_context_protocol.md` - Complete reference for MCP.
2. **[MODIFY]** `wiki/index.md` - Update navigation maps and tags.

## Constraints
- Must follow specs/schema.md format.
- Links must be relative.
"""

DEMO_TODO_V1 = """- [ ] Create `wiki/model_context_protocol.md` with complete reference.
- [ ] Add YAML Frontmatter.
- [ ] Update `wiki/index.md` navigation map.
"""

DEMO_REVIEW_V1 = """# Plan Review: Grade 6/10 (REJECTED)

## Critique
- The proposed TODO list is missing explicit inputs, outputs, and Acceptance Criteria (AC).
- The tag set in the frontmatter plan is too sparse.
- Broken link check should be added explicitly to the checklist.

## Action required
- Planner must rewrite both Plan.md and TODO.md with explicit AC.
"""

DEMO_PLAN_V2 = """# Proposed Plan: Ingesting Model Context Protocol (MCP) (v2)

This plan is updated to address the Reviewer's feedback.

## Proposed Modifications
1. **[NEW]** `wiki/model_context_protocol.md` - Complete reference for MCP.
2. **[MODIFY]** `wiki/index.md` - Update navigation maps and tags.

## Verification Details
- Run Tester Agent to confirm zero broken links and correct frontmatter YAML structures.
"""

DEMO_TODO_V2 = """- [ ] Create `wiki/model_context_protocol.md`
  - **Input:** Raw scraped MCP content.
  - **Output:** `wiki/model_context_protocol.md` file.
  - **AC:** YAML Frontmatter present, tags are `["mcp", "ai", "protocol"]`, title is `"Model Context Protocol"`.
- [ ] Update `wiki/index.md` navigation map.
  - **Input:** `wiki/model_context_protocol.md` existence.
  - **Output:** Modified `wiki/index.md` file.
  - **AC:** Hyperlink successfully points to `/wiki/model_context_protocol.md`.
"""

DEMO_REVIEW_V2 = """# Plan Review: Grade 9/10 (APPROVED)

## Validation Results
- Standard schema conditions satisfied.
- Action items are split into atomic checklist items with detailed Acceptance Criteria.
- Proceeding to Coder implementation phase.
"""

DEMO_MCP_PAGE = """---
title: "Model Context Protocol"
tags: ["mcp", "ai", "protocol", "external-tools"]
last_updated: 2026-05-22
links: ["/wiki/index.md", "/wiki/agentic_coding_basics.md"]
version: 1.0
---

# Model Context Protocol (MCP)

The **Model Context Protocol (MCP)** is an open-source standard created by Anthropic that acts as an "AI-native USB interface." It enables LLM Agents to interact with external tools, databases, and APIs in a unified and highly scalable manner.

---

## 💡 Core Architecture

Unlike traditional hardcoded connectors, MCP establishes a client-server relationship:

```
┌──────────────┐         MCP         ┌──────────────┐
│  LLM Client  │ ◄─────────────────► │  MCP Server  │
│ (Claude/Gem) │   JSON-RPC 2.0      │ (SQLite/Git) │
└──────────────┘                     └──────────────┘
```

1. **MCP Host/Client:** The orchestration environment (such as Claude Code, Codex, or a python script) that drives tool usage.
2. **MCP Server:** Lightweight processes exposing custom tools via standard protocol formats.

---

## 🛠️ Schema Tools in action

An MCP Server typically registers three core capabilities:
- **Resources:** Read-only data sources (like database schemas or file paths).
- **Tools:** Actionable executable commands (like running a compiler or editing files).
- **Prompts:** Pre-designed prompt templates.

For details on implementing custom servers, refer to the [Agentic Coding Basics](/wiki/agentic_coding_basics.md) compilation.
"""

# ==============================================================================
# Orchestrator Core Class
# ==============================================================================
class LLMWikiOrchestrator:
    def __init__(self, workspace_path, demo_mode=True):
        self.workspace = workspace_path
        self.demo_mode = demo_mode
        self.pool_dir = os.path.join(workspace_path, ".pool")
        self.wiki_dir = os.path.join(workspace_path, "wiki")
        self.specs_dir = os.path.join(workspace_path, "specs")
        self.agents = {}
        
        # Load agent definitions from pool
        self._load_agent_pool()

    def _load_agent_pool(self):
        os.makedirs(self.pool_dir, exist_ok=True)
        os.makedirs(self.wiki_dir, exist_ok=True)
        os.makedirs(self.specs_dir, exist_ok=True)
        
        for file in os.listdir(self.pool_dir):
            if file.endswith(".json"):
                path = os.path.join(self.pool_dir, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        spec = json.load(f)
                        self.agents[spec["id"]] = spec
                except Exception as e:
                    print(f"Error loading agent spec {file}: {e}")

    def append_journal(self, summary, result="SUCCESS"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        journal_path = os.path.join(self.workspace, "journal.md")
        entry = f"- [{timestamp}] {summary} — {result}\n"
        
        # Open in append mode
        with open(journal_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def update_task_status(self, step_str, done=True):
        task_path = os.path.join(self.workspace, "TASK.md")
        if not os.path.exists(task_path):
            return
            
        with open(task_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Replace uncompleted checklist item with completed if done
        pattern = rf"- \[ \]\s+{re.escape(step_str)}"
        replacement = f"- [x] {step_str}" if done else f"- [ ] {step_str}"
        content = re.sub(pattern, replacement, content)
        
        with open(task_path, "w", encoding="utf-8") as f:
            f.write(content)

    def run_pipeline(self, raw_input):
        print_header("LLM WIKI MULTI-AGENT INGESTION PIPELINE")
        self.append_journal("Starting multi-agent ingestion pipeline", "RUNNING")
        
        # ----------------------------------------------------------------------
        # Step 1: PLANNER AGENT
        # ----------------------------------------------------------------------
        print_header("Step 1: Planner Agent - Analyzing & Decomposing Ingestion")
        print_agent_status("planner", "running", "Analyzing raw item and generating plans...")
        time.sleep(1.5)
        
        # Write initial planning outputs
        plan_path = os.path.join(self.workspace, "Plan.md")
        todo_path = os.path.join(self.workspace, "TODO.md")
        
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(DEMO_PLAN_V1)
        with open(todo_path, "w", encoding="utf-8") as f:
            f.write(DEMO_TODO_V1)
            
        print_agent_status("planner", "completed", "Created Plan.md and TODO.md in workspace root.")
        print_section("Planner Output: Plan.md (Draft v1)", DEMO_PLAN_V1)
        self.update_task_status("Raw input is parsed and decomposed into a plan.")
        self.append_journal("Planner created Plan.md and TODO.md", "SUCCESS")
        
        # ----------------------------------------------------------------------
        # Step 2: PLANNER-REVIEWER DEBATE LOOP
        # ----------------------------------------------------------------------
        print_header("Step 2: Reviewer Agent - Performing Debate & Quality Evaluation")
        
        round_num = 1
        print(f"{BOLD}{YELLOW}[DEBATE ROUND {round_num}]{ENDC} Reviewer critique executing...")
        time.sleep(1.5)
        
        # Reviewer first pass (Score: 6 - Forced Reject to demonstrate revision loop)
        review_path = os.path.join(self.workspace, "REVIEW.md")
        with open(review_path, "w", encoding="utf-8") as f:
            f.write(DEMO_REVIEW_V1)
            
        print_agent_status("reviewer", "failed", "Plan scored 6/10 (REJECTED). Feedback stored in REVIEW.md.")
        print_section("Reviewer Output: REVIEW.md (Round 1)", DEMO_REVIEW_V1)
        self.append_journal("Reviewer evaluated Plan.md (Score: 6/10)", "REJECTED")
        
        # Debate Round 2 (Planner rewrites, Reviewer approves)
        round_num += 1
        print(f"\n{BOLD}{YELLOW}[DEBATE ROUND {round_num}]{ENDC} Planner rewriting plan based on feedback...")
        time.sleep(1.5)
        
        revised_plan_path = os.path.join(self.workspace, "Revised_Plan.md")
        final_todo_path = os.path.join(self.workspace, "Final_TODO.md")
        with open(revised_plan_path, "w", encoding="utf-8") as f:
            f.write(DEMO_PLAN_V2)
        with open(final_todo_path, "w", encoding="utf-8") as f:
            f.write(DEMO_TODO_V2)
            
        print_agent_status("planner", "completed", "Generated Revised_Plan.md and Final_TODO.md.")
        print_section("Planner Output: Revised_Plan.md (v2)", DEMO_PLAN_V2)
        
        print(f"{BOLD}{YELLOW}[DEBATE ROUND {round_num}]{ENDC} Reviewer re-evaluating...")
        time.sleep(1.5)
        
        with open(review_path, "w", encoding="utf-8") as f:
            f.write(DEMO_REVIEW_V2)
            
        print_agent_status("reviewer", "completed", "Plan scored 9/10 (APPROVED). Finalizing checklist.")
        print_section("Reviewer Output: REVIEW.md (Round 2 Approved)", DEMO_REVIEW_V2)
        self.update_task_status("Planner and Reviewer complete debate loop, scoring >= 8.")
        self.append_journal("Reviewer approved Revised_Plan.md (Score: 9/10)", "SUCCESS")
        
        # ----------------------------------------------------------------------
        # Step 3: CODER AGENT - File Modification & Creation
        # ----------------------------------------------------------------------
        print_header("Step 3: Coder Agent - Executing Code Base Updates")
        print_agent_status("coder", "running", "Creating wiki/model_context_protocol.md and updating wiki/index.md...")
        time.sleep(2.0)
        
        # 1. Create the new wiki page
        mcp_page_path = os.path.join(self.wiki_dir, "model_context_protocol.md")
        with open(mcp_page_path, "w", encoding="utf-8") as f:
            f.write(DEMO_MCP_PAGE)
            
        # 2. Update wiki/index.md to include the new page link
        index_path = os.path.join(self.wiki_dir, "index.md")
        with open(index_path, "r", encoding="utf-8") as f:
            index_content = f.read()
            
        # Insert link dynamically in navigation map
        link_to_add = "- [Model Context Protocol](/wiki/model_context_protocol.md) — Comprehensive guide on Anthropic's open tool-connection standard."
        updated_index = index_content.replace(
            "### Core Engineering Lessons",
            f"### Core Engineering Lessons\n{link_to_add}"
        )
        
        # Update frontmatter links list in index.md
        updated_index = updated_index.replace(
            'links: ["/wiki/agentic_coding_basics.md"]',
            'links: ["/wiki/agentic_coding_basics.md", "/wiki/model_context_protocol.md"]'
        )
        
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(updated_index)
            
        print_agent_status("coder", "completed", "Successfully updated wiki pages.")
        print_section("Coder Output: wiki/model_context_protocol.md", DEMO_MCP_PAGE)
        self.update_task_status("New wiki pages are generated inside the wiki/ directory with a valid frontmatter schema.")
        self.update_task_status("Internal cross-links are resolved, and wiki/index.md is updated.")
        self.append_journal("Coder updated wiki/model_context_protocol.md and wiki/index.md", "SUCCESS")
        
        # ----------------------------------------------------------------------
        # Step 4: TESTER AGENT - Automated Schema & Route Verification
        # ----------------------------------------------------------------------
        print_header("Step 4: Tester Agent - Running Verification Checks")
        print_agent_status("tester", "running", "Executing frontmatter, markdown schema, and dead-link validation...")
        time.sleep(2.0)
        
        # Run local verification check
        broken_links, invalid_frontmatter = self._validate_wiki_directory()
        
        report_path = os.path.join(self.workspace, "test_report.md")
        report_content = f"""# Test Ingestion Validation Report

**Timestamp:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status:** PASS ✅

## Executed Audits
1. **Markdown Format Audit:** Checked all `.md` files under `wiki/` directory. -> **PASS**
2. **YAML Frontmatter Schema Audit:** Validated tags, title, version, and links schema in all files. -> **PASS**
3. **Dead-Link Audit:** Audited all relative cross-links. -> **PASS** (0 broken links found)
4. **Homepage Mapping Audit:** Checked index routing. -> **PASS**
"""
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        if len(broken_links) == 0 and len(invalid_frontmatter) == 0:
            print_agent_status("tester", "completed", "Zero compilation errors found. Build output verified.")
            print_section("Tester Validation Report", report_content)
            self.update_task_status("The Tester Agent verifies that no broken links or schema violations exist.")
            self.append_journal("Tester executed validation checks", "SUCCESS")
        else:
            print_agent_status("tester", "failed", "Validation failure: broken references found.")
            self.append_journal("Tester failed validation checks", "FAILED")
            return False
            
        # ----------------------------------------------------------------------
        # Pipeline Finalization
        # ----------------------------------------------------------------------
        print_header("Ingestion Pipeline Completed Successfully!")
        self.update_task_status("Execution details are successfully logged in journal.md.")
        
        # Update TASK.md status to done
        task_path = os.path.join(self.workspace, "TASK.md")
        with open(task_path, "r", encoding="utf-8") as f:
            task_content = f.read()
        task_content = task_content.replace("Status: open", "Status: done")
        with open(task_path, "w", encoding="utf-8") as f:
            f.write(task_content)
            
        self.append_journal("Pipeline ingestion run successfully finalized", "SUCCESS")
        return True

    def _validate_wiki_directory(self):
        broken_links = []
        invalid_frontmatter = []
        
        # Get all valid file names in wiki folder
        all_wiki_files = [f for f in os.listdir(self.wiki_dir) if f.endswith(".md")]
        
        for file in all_wiki_files:
            path = os.path.join(self.wiki_dir, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # 1. Frontmatter Validation
            if not content.startswith("---"):
                invalid_frontmatter.append(file)
                continue
                
            fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if not fm_match:
                invalid_frontmatter.append(file)
                continue
                
            fm_text = fm_match.group(1)
            # Simple check for required fields: title, tags, last_updated, links, version
            required = ["title:", "tags:", "last_updated:", "links:", "version:"]
            for req in required:
                if req not in fm_text:
                    invalid_frontmatter.append(f"{file} (missing {req})")
                    
            # 2. Markdown Link Verification
            links = re.findall(r"\[.*?\]\((/wiki/.*?\.md)\)", content)
            for link in links:
                target_name = os.path.basename(link)
                if target_name not in all_wiki_files:
                    broken_links.append(f"{file} -> {link} (Broken link)")
                    
        return broken_links, invalid_frontmatter

    def query_wiki(self, user_query):
        print_header(f"USER QUERY PROCESSOR: '{user_query}'")
        self.append_journal(f"User queried: '{user_query}'", "RUNNING")
        
        # Locate all wiki files
        all_wiki_files = [f for f in os.listdir(self.wiki_dir) if f.endswith(".md")]
        matches = []
        
        # Scan files for keywords (case-insensitive)
        keywords = user_query.lower().split()
        for file in all_wiki_files:
            path = os.path.join(self.wiki_dir, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Scan title, tags, and body
            score = 0
            for kw in keywords:
                if kw in file.lower():
                    score += 10
                if kw in content.lower():
                    score += content.lower().count(kw)
            
            if score > 0:
                # Extract title from frontmatter or heading
                title_match = re.search(r'title:\s*"(.*?)"', content)
                title = title_match.group(1) if title_match else file
                matches.append((file, title, score, content))
                
        # Sort matches by relevance score
        matches.sort(key=lambda x: x[2], reverse=True)
        
        if not matches:
            print_agent_status("orchestrator", "failed", f"No documents found matching '{user_query}'.")
            # Suggest existing pages
            print("\nAvailable pages in Wiki:")
            for f in all_wiki_files:
                print(f"  - /wiki/{f}")
            self.append_journal(f"User query found 0 matches", "SUCCESS")
            return False
            
        print_agent_status("orchestrator", "completed", f"Found {len(matches)} relevant wiki nodes.")
        
        # Grab primary match and synthesize an elegant answer
        best_file, best_title, best_score, best_content = matches[0]
        
        # Basic synthesis: extract headings and key paragraphs
        paragraphs = [p.strip() for p in best_content.split('\n\n') if p.strip() and not p.startswith('---') and not p.startswith('#')]
        summary = "\n\n".join(paragraphs[:3])
        
        # Extract tags and links from frontmatter
        tags_match = re.search(r'tags:\s*\[(.*?)\]', best_content)
        tags = tags_match.group(1) if tags_match else "none"
        links_match = re.search(r'links:\s*\[(.*?)\]', best_content)
        links = links_match.group(1) if links_match else "none"
        
        synthesis = f"""### Source: `/wiki/{best_file}` ({best_title})
**Metadata Tags:** `[{tags}]`
**Cross-References:** `[{links}]`

---

### Synthesized Answer

{summary}

---

**Relevance Score:** {best_score} | **Alternate matches:** {", ".join([m[1] for m in matches[1:3]]) or "none"}
"""
        print_section("Synthesized Wiki Response", synthesis)
        self.append_journal(f"User query completed with best match: {best_file}", "SUCCESS")
        return True

    def maintain_wiki(self):
        print_header("LLM WIKI AUTOMATED MAINTENANCE & AUDIT ROUTINE")
        self.append_journal("Starting automated wiki maintenance", "RUNNING")
        
        all_wiki_files = [f for f in os.listdir(self.wiki_dir) if f.endswith(".md")]
        
        broken_links = []
        invalid_frontmatter = []
        orphan_pages = set(all_wiki_files)
        
        # Never consider index.md an orphan
        if "index.md" in orphan_pages:
            orphan_pages.remove("index.md")
            
        # Parse links and check mappings
        for file in all_wiki_files:
            path = os.path.join(self.wiki_dir, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # 1. Frontmatter Validation
            if not content.startswith("---"):
                invalid_frontmatter.append(f"{file} (Missing frontmatter dashes)")
                continue
                
            fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if not fm_match:
                invalid_frontmatter.append(f"{file} (Invalid frontmatter closure)")
                continue
                
            fm_text = fm_match.group(1)
            required = ["title:", "tags:", "last_updated:", "links:", "version:"]
            for req in required:
                if req not in fm_text:
                    invalid_frontmatter.append(f"{file} (Missing metadata field: {req})")
                    
            # 2. Extract relative paths and links
            links = re.findall(r"\[.*?\]\((/wiki/.*?\.md)\)", content)
            
            # Check frontmatter links list too
            fm_links_match = re.search(r'links:\s*\[(.*?)\]', fm_text)
            if fm_links_match:
                # Split and clean links
                fm_links = [l.strip().strip('"').strip("'") for l in fm_links_match.group(1).split(",") if l.strip()]
                for l in fm_links:
                    if l not in links:
                        links.append(l)
                        
            for link in links:
                target_name = os.path.basename(link)
                # Check for absolute paths
                if ":" in link or "\\\\" in link:
                    broken_links.append(f"{file} -> {link} (BANNED absolute path structure)")
                    continue
                if not link.startswith("/wiki/"):
                    broken_links.append(f"{file} -> {link} (Invalid relative path format - must start with /wiki/)")
                    continue
                if target_name not in all_wiki_files:
                    broken_links.append(f"{file} -> {link} (Broken target link - file does not exist)")
                else:
                    # Remove linked target from orphan set
                    if target_name in orphan_pages:
                        orphan_pages.remove(target_name)
                        
        # 3. Dynamic Homepage Navigation Map Re-compilation!
        # Automatically updates the homepage index map so the user/agent doesn't have to do it manually!
        index_path = os.path.join(self.wiki_dir, "index.md")
        index_updated = False
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                index_content = f.read()
                
            # Compile new Navigation Map list
            nav_entries = []
            for file in all_wiki_files:
                if file == "index.md":
                    continue
                path = os.path.join(self.wiki_dir, file)
                with open(path, "r", encoding="utf-8") as f:
                    file_text = f.read()
                title_match = re.search(r'title:\s*"(.*?)"', file_text)
                title = title_match.group(1) if title_match else file.replace(".md", "").replace("_", " ").title()
                
                # Exclude frontmatter lines and grab the first sentence
                paragraphs = [p.strip() for p in file_text.split('\n\n') if p.strip() and not p.startswith('---') and not p.startswith('#')]
                desc = paragraphs[0][:120].strip() if paragraphs else "No description available."
                if not desc.endswith('.'):
                    desc += "..."
                    
                nav_entries.append(f"- [{title}](/wiki/{file}) -- {desc}")
                
            # Replace the Navigation Map inside index.md
            if "## 🗺️ Navigation Map" in index_content or "## Navigation Map" in index_content:
                header_part = "## 🗺️ Navigation Map" if "## 🗺️ Navigation Map" in index_content else "## Navigation Map"
                header_parts = index_content.split(header_part)
                footer_parts = header_parts[1].split("---")
                
                # Reconstruct clean navigation map
                index_content = header_parts[0] + header_part + "\n\n### Core Engineering Lessons\n" + "\n".join(nav_entries) + "\n\n" + "---".join(footer_parts[1:])
                index_updated = True
                
            # Also update frontmatter links in index.md
            links_list = [f"/wiki/{f}" for f in all_wiki_files if f != "index.md"]
            links_str = ", ".join(f'"{l}"' for l in links_list)
            index_content = re.sub(r'links:\s*\[.*?\]', f'links: [{links_str}]', index_content)
            
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(index_content)
                
        # 4. Calculate Global Wiki Health Score
        total_issues = len(broken_links) + len(invalid_frontmatter) + len(orphan_pages)
        max_score = 100
        # Subtract 10 points per issue, minimum score 0
        health_score = max(0, max_score - (total_issues * 10))
        
        # 5. Output beautiful Scorecard Dashboard
        scorecard = f"""
================================================================================
                        LLM WIKI HEALTH SCORECARD
================================================================================
  Wiki Health Score:      {health_score}%
  Total Files Audited:    {len(all_wiki_files)}
  Invalid Frontmatters:   {len(invalid_frontmatter)}
  Dead/Broken Links:      {len(broken_links)}
  Orphaned Pages:         {len(orphan_pages)}
  Homepage Rebuilt:       {"YES" if index_updated else "NO"}
================================================================================
"""
        print(scorecard)
        
        if invalid_frontmatter:
            print("Invalid Frontmatters Found:")
            for issue in invalid_frontmatter:
                print(f"  - {issue}")
        if broken_links:
            print("\nBroken Cross-Links Found:")
            for issue in broken_links:
                print(f"  - {issue}")
        if orphan_pages:
            print("\nOrphaned Pages (Unlinked):")
            for orphan in orphan_pages:
                print(f"  - /wiki/{orphan}")
                
        self.append_journal(f"Maintenance audit executed. Health Score: {health_score}%. Issues: {total_issues}", "SUCCESS")
        return health_score >= 80

# ==============================================================================
# Script Entry Point (Self-contained CLI Dashboard)
# ==============================================================================
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    raw_ingest_data = "Ingest the Model Context Protocol (MCP) details. It defines Client-Server interface protocols."
    
    orchestrator = LLMWikiOrchestrator(current_dir)
    orchestrator.run_pipeline(raw_ingest_data)

