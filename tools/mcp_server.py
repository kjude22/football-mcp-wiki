import os
import re
import yaml
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Football Wiki Server")

# Paths configuration (relative to parent directory of tools/ folder)
WIKI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")

def _get_page_path(page_name: str) -> str:
    """Helper to sanitize and return file path."""
    if not page_name.endswith(".md"):
        page_name += ".md"
    # Prevent directory traversal
    basename = os.path.basename(page_name).lower()
    return os.path.join(WIKI_DIR, basename)

@mcp.tool()
def search_wiki(query: str) -> str:
    """Search pages in the Football Wiki by keywords. Returns matching page names and previews."""
    if not os.path.exists(WIKI_DIR):
        return "Wiki directory not found."
    
    results = []
    keywords = query.lower().split()
    for file in os.listdir(WIKI_DIR):
        if not file.endswith(".md"):
            continue
        path = os.path.join(WIKI_DIR, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            score = 0
            for kw in keywords:
                if kw in file.lower():
                    score += 10
                if kw in content.lower():
                    score += content.lower().count(kw)
            if score > 0:
                # Find title
                title_match = re.search(r'title:\s*"(.*?)"', content)
                title = title_match.group(1) if title_match else file
                results.append((file, title, score))
        except Exception as e:
            pass
            
    if not results:
        return f"No pages matched the query '{query}'."
        
    results.sort(key=lambda x: x[2], reverse=True)
    out = [f"Found {len(results)} matches:"]
    for file, title, score in results[:5]:
        out.append(f"- [{title}](/wiki/{file}) (Score: {score})")
    return "\n".join(out)

@mcp.tool()
def read_wiki_page(page_name: str) -> str:
    """Read the full content of a wiki page (including metadata frontmatter) by its filename."""
    path = _get_page_path(page_name)
    if not os.path.exists(path):
        return f"Error: Page '{page_name}' does not exist in the wiki."
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading page: {str(e)}"

@mcp.tool()
def write_wiki_page(page_name: str, title: str, tags: list[str], links: list[str], content: str) -> str:
    """Create or update a wiki page with valid YAML frontmatter metadata and markdown content.
    Automatically handles schema format validation and increments version numbers if existing.
    """
    path = _get_page_path(page_name)
    os.makedirs(WIKI_DIR, exist_ok=True)
    
    # Clean tags and links
    tags = [t.lower().strip() for t in tags if t.strip()]
    links = [l.strip() for l in links if l.strip()]
    
    # Calculate version
    version = 1.0
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = f.read()
            ver_match = re.search(r'version:\s*([0-9.]+)', existing)
            if ver_match:
                version = round(float(ver_match.group(1)) + 0.1, 1)
        except Exception:
            pass
            
    # Formulate YAML frontmatter
    frontmatter = {
        "title": title,
        "tags": tags,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "links": links,
        "version": version
    }
    
    # Format YAML with double quotes on title to fit requirements
    yaml_lines = [
        "---",
        f'title: "{title}"',
        f'tags: {tags}',
        f'last_updated: {frontmatter["last_updated"]}',
        f'links: {links}',
        f'version: {version}',
        "---",
        ""
    ]
    
    # If the content doesn't start with a clean title header, insert one
    clean_content = content.strip()
    if not clean_content.startswith("#"):
        clean_content = f"# {title}\n\n{clean_content}"
        
    full_file_content = "\n".join(yaml_lines) + clean_content + "\n"
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(full_file_content)
        return f"Success: Page '{page_name}' written successfully (Version {version})."
    except Exception as e:
        return f"Error writing page: {str(e)}"

@mcp.tool()
def verify_wiki_health() -> str:
    """Run an automated audit on the wiki directory.
    Validates frontmatter, checks for broken relative links, finds orphaned pages,
    and returns a summary with a Health Score.
    """
    if not os.path.exists(WIKI_DIR):
        return "Wiki directory not found."
        
    all_files = [f for f in os.listdir(WIKI_DIR) if f.endswith(".md")]
    broken_links = []
    invalid_frontmatter = []
    orphan_pages = set(all_files)
    
    if "index.md" in orphan_pages:
        orphan_pages.remove("index.md")
        
    for file in all_files:
        path = os.path.join(WIKI_DIR, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Validate frontmatter dashes
            if not content.startswith("---"):
                invalid_frontmatter.append(f"{file} (Missing start dashes)")
                continue
                
            fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if not fm_match:
                invalid_frontmatter.append(f"{file} (Invalid frontmatter structure)")
                continue
                
            fm_text = fm_match.group(1)
            # Check fields
            fields = ["title:", "tags:", "last_updated:", "links:", "version:"]
            for field in fields:
                if field not in fm_text:
                    invalid_frontmatter.append(f"{file} (Missing '{field[:-1]}')")
                    
            # Parse links in markdown: [Text](/wiki/target.md)
            links = re.findall(r"\[.*?\]\((/wiki/.*?\.md)\)", content)
            
            # Also parse frontmatter links lists
            fm_links_match = re.search(r'links:\s*\[(.*?)\]', fm_text)
            if fm_links_match:
                fm_links = [l.strip().strip('"').strip("'") for l in fm_links_match.group(1).split(",") if l.strip()]
                for fl in fm_links:
                    if fl not in links:
                        links.append(fl)
                        
            # Verify each link
            for link in links:
                target = os.path.basename(link)
                if ":" in link or "\\\\" in link:
                    broken_links.append(f"{file} -> {link} (Banned absolute path)")
                    continue
                if not link.startswith("/wiki/"):
                    broken_links.append(f"{file} -> {link} (Must start with /wiki/)")
                    continue
                if target not in all_files:
                    broken_links.append(f"{file} -> {link} (File does not exist)")
                else:
                    if target in orphan_pages:
                        orphan_pages.remove(target)
        except Exception as e:
            invalid_frontmatter.append(f"{file} (Read error: {str(e)})")
            
    total_issues = len(broken_links) + len(invalid_frontmatter) + len(orphan_pages)
    health_score = max(0, 100 - (total_issues * 10))
    
    out = [
        "=== WIKI HEALTH REPORT ===",
        f"Health Score: {health_score}%",
        f"Total Files Audited: {len(all_files)}",
        f"Malformed Frontmatters: {len(invalid_frontmatter)}",
        f"Broken Links: {len(broken_links)}",
        f"Orphaned Pages: {len(orphan_pages)}",
        "========================="
    ]
    if invalid_frontmatter:
        out.append("\nMalformed Frontmatter Files:")
        for issue in invalid_frontmatter:
            out.append(f"  - {issue}")
    if broken_links:
        out.append("\nBroken Links Found:")
        for link in broken_links:
            out.append(f"  - {link}")
    if orphan_pages:
        out.append("\nOrphaned Pages (unreferenced):")
        for orphan in orphan_pages:
            out.append(f"  - /wiki/{orphan}")
            
    return "\n".join(out)

if __name__ == "__main__":
    # Start the FastMCP server (defaults to stdio communication for integration)
    mcp.run()
