import os
import re
import sys

def audit_wiki(wiki_dir):
    if not os.path.exists(wiki_dir):
        print(f"Error: Wiki directory '{wiki_dir}' does not exist.")
        return False

    all_files = [f for f in os.listdir(wiki_dir) if f.endswith(".md")]
    broken_links = []
    invalid_frontmatter = []
    
    for file in all_files:
        path = os.path.join(wiki_dir, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Verify YAML frontmatter syntax
            if not content.startswith("---"):
                invalid_frontmatter.append(f"{file} (Missing start dashes)")
                continue
                
            fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if not fm_match:
                invalid_frontmatter.append(f"{file} (Invalid frontmatter structure)")
                continue
                
            fm_text = fm_match.group(1)
            fields = ["title:", "tags:", "last_updated:", "links:", "version:"]
            for field in fields:
                if field not in fm_text:
                    invalid_frontmatter.append(f"{file} (Missing '{field[:-1]}')")
                    
            # Parse links in markdown
            links = re.findall(r"\[.*?\]\((/wiki/.*?\.md)\)", content)
            
            # Parse links in frontmatter list
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
        except Exception as e:
            invalid_frontmatter.append(f"{file} (Read error: {str(e)})")
            
    total_issues = len(broken_links) + len(invalid_frontmatter)
    health_score = max(0, 100 - (total_issues * 10))
    
    print("=== HARNESS SYNTAX AUDIT REPORT ===")
    print(f"Health Score: {health_score}%")
    print(f"Total Files Checked: {len(all_files)}")
    print(f"Malformed Frontmatters: {len(invalid_frontmatter)}")
    print(f"Broken Internal Links: {len(broken_links)}")
    print("===================================")
    
    if invalid_frontmatter:
        print("\nInvalid Frontmatter Details:")
        for issue in invalid_frontmatter:
            print(f"  - {issue}")
            
    if broken_links:
        print("\nBroken Link Details:")
        for link in broken_links:
            print(f"  - {link}")
            
    return total_issues == 0

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # wiki folder is located at ../../wiki relative to this script
    wiki_folder = os.path.join(current_dir, "..", "..", "wiki")
    success = audit_wiki(wiki_folder)
    sys.exit(0 if success else 1)
