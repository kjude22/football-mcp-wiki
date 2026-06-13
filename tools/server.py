import os
import json
import re
from http.server import SimpleHTTPRequestHandler, HTTPServer
import mcp_server  # Programmatic import of the FastMCP tools
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables using absolute path to prevent CWD mismatch (pointing to parent folder)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=env_path)

PORT = 8000
GUI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gui")
WIKI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
SCHEMA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schema", "schema.md")

# Configure Gemini API key
api_key = os.environ.get("GEMINI_API_KEY")
has_gemini = False
chat_session = None

# Gemini Tool Wrappers (with type hints and docstrings for Gemini model schema generation)
def search_wiki(query: str) -> str:
    """Search football pages in the Wiki database by keywords. Returns matching page names."""
    return mcp_server.search_wiki(query)

def read_wiki_page(page_name: str) -> str:
    """Read the full content of a wiki page (including metadata frontmatter) by its name."""
    return mcp_server.read_wiki_page(page_name)

def write_wiki_page(page_name: str, title: str, tags: list[str], links: list[str], content: str) -> str:
    """Create or update a wiki page with valid YAML frontmatter metadata and content.
    Links must be relative root-based paths (e.g. ['/wiki/tottenham_hotspur.md']).
    """
    return mcp_server.write_wiki_page(page_name, title, tags, links, content)

def verify_wiki_health() -> str:
    """Verify that there are no broken relative links or invalid frontmatter. Returns a Health Scorecard."""
    return mcp_server.verify_wiki_health()

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=[search_wiki, read_wiki_page, write_wiki_page, verify_wiki_health],
            system_instruction=(
                "You are FootyAgent, the LLM Wiki Programmer responsible for maintaining the football wiki database (wiki/ folder).\n"
                "The wiki is a persistent codebase of knowledge. Your job is to search the wiki, read pages, and write/edit wiki pages to compile facts continuously.\n"
                "When the user asks a question, ALWAYS search and read the relevant wiki pages FIRST using `search_wiki` and `read_wiki_page` to compile facts before replying.\n"
                "If information is missing, or if the user asks you to add/modify pages, use `write_wiki_page` to create or update the page so the knowledge is permanently compiled in the wiki.\n"
                "Ensure pages have double-quoted titles in the YAML frontmatter, and maintain bidirectional relative links in the `links` list (e.g. if page A links to B, page B links to A).\n"
                "After writing pages, always run `verify_wiki_health` to verify that there are no broken links.\n"
                "Reply in Korean."
            )
        )
        chat_session = model.start_chat(enable_automatic_function_calling=True)
        has_gemini = True
        print("Gemini API Client successfully initialized with Local FastMCP tools.")
    except Exception as e:
        print("Error initializing Gemini API:", e)
        has_gemini = False


def run_local_fallback(message: str, tool_calls: list, prefix: str) -> str:
    msg_lower = message.lower()
    
    # Translation map for Korean terms to English counterparts for searching
    translation_map = {
        "손흥민": "son",
        "메시": "messi",
        "호날두": "ronaldo",
        "음바페": "mbappe",
        "홀란드": "haaland",
        "덕배": "de bruyne",
        "데 브라이너": "de bruyne",
        "데브라이너": "de bruyne",
        "케인": "kane",
        "해리 케인": "kane",
        "벨링엄": "bellingham",
        "주드 벨링엄": "bellingham",
        "살라": "salah",
        "모하메드 살라": "salah",
        "반다이크": "van dijk",
        "네이마르": "neymar",
        "레반도프스키": "lewandowski",
        "토트넘": "tottenham",
        "레알": "real madrid",
        "레알 마드리드": "real madrid",
        "바르샤": "barcelona",
        "바르셀로나": "barcelona",
        "맨시티": "manchester city",
        "맨체스터 시티": "manchester city",
        "리버풀": "liverpool",
        "맨유": "manchester united",
        "맨체스터 유나이티드": "manchester united",
        "뮌헨": "bayern munich",
        "바이에른 뮌헨": "bayern munich",
        "파리": "paris",
        "파리 생제르맹": "paris saint germain",
        "아스날": "arsenal",
        "첼시": "chelsea",
        "게겐프레싱": "gegenpressing",
        "티키타카": "tiki taka",
        "카테나치오": "catenaccio",
        "텐백": "park the bus",
        "버스 세우기": "park the bus",
        "폴스나인": "false nine",
        "펄스나인": "false nine",
        "가짜 9번": "false nine",
        "프리미어리그": "premier league",
        "라리가": "la liga",
        "세리에": "serie a"
    }
    
    # 1. Search Wiki
    if any(k in msg_lower for k in ["search", "find", "검색", "찾아", "찾기"]):
        query = message
        for word in ["search", "find", "검색", "찾아", "찾기", "해줘", "해봐"]:
            query = re.sub(rf"\b{word}\b", "", query, flags=re.IGNORECASE).replace(word, "")
        query = query.strip().strip("'").strip('"')
        
        # Translate query if it is in Korean
        search_query = query.lower()
        for kor, eng in translation_map.items():
            if kor in search_query:
                search_query = search_query.replace(kor, eng)
                
        tool_calls.append({
            "tool": "search_wiki",
            "arguments": {"query": search_query}
        })
        res = mcp_server.search_wiki(search_query)
        return prefix + f"에이전트가 MCP 도구 **search_wiki**를 실행해 '{query}'(번역: '{search_query}') 관련 정보를 검색했습니다:\n\n{res}"
        
    # 2. Verify Wiki Health
    elif any(k in msg_lower for k in ["health", "verify", "check", "건강", "검사", "점검", "상태"]):
        tool_calls.append({
            "tool": "verify_wiki_health",
            "arguments": {}
        })
        res = mcp_server.verify_wiki_health()
        return prefix + f"에이전트가 MCP 도구 **verify_wiki_health**를 실행하여 위키 무결성 감사를 실행했습니다:\n\n```text\n{res}\n```"
        
    # 3. Read Wiki Page
    elif any(k in msg_lower for k in ["read", "get", "읽", "조회", "열기"]):
        page = message
        for word in ["read", "get", "읽어", "읽기", "조회", "열기", "해줘"]:
            page = re.sub(rf"\b{word}\b", "", page, flags=re.IGNORECASE).replace(word, "")
        page = page.lower().replace(".md", "").strip()
        
        page_map = {
            "손흥민": "son_heung_min",
            "son": "son_heung_min",
            "메시": "lionel_messi",
            "messi": "lionel_messi",
            "호날두": "cristiano_ronaldo",
            "ronaldo": "cristiano_ronaldo",
            "음바페": "kylian_mbappe",
            "mbappe": "kylian_mbappe",
            "홀란드": "erling_haaland",
            "haaland": "erling_haaland",
            "덕배": "kevin_de_bruyne",
            "데브라이너": "kevin_de_bruyne",
            "데 브라이너": "kevin_de_bruyne",
            "케인": "harry_kane",
            "kane": "harry_kane",
            "벨링엄": "jude_bellingham",
            "bellingham": "jude_bellingham",
            "살라": "mohamed_salah",
            "salah": "mohamed_salah",
            "반다이크": "virgil_van_dijk",
            "van dijk": "virgil_van_dijk",
            "네이마르": "neymar_jr",
            "neymar": "neymar_jr",
            "레반도프스키": "robert_lewandowski",
            "lewandowski": "robert_lewandowski",
            "토트넘": "tottenham_hotspur",
            "tottenham": "tottenham_hotspur",
            "spurs": "tottenham_hotspur",
            "레알": "real_madrid",
            "real madrid": "real_madrid",
            "바르샤": "barcelona",
            "바르셀로나": "barcelona",
            "맨시티": "manchester_city",
            "manchester city": "manchester_city",
            "리버풀": "liverpool",
            "맨유": "manchester_united",
            "manchester united": "manchester_united",
            "뮌헨": "bayern_munich",
            "bayern munich": "bayern_munich",
            "파리": "paris_saint_germain",
            "paris saint germain": "paris_saint_germain",
            "psg": "paris_saint_germain",
            "아스날": "arsenal",
            "첼시": "chelsea",
            "게겐프레싱": "gegenpressing",
            "gegenpressing": "gegenpressing",
            "티키타카": "tiki_taka",
            "티키 타카": "tiki_taka",
            "카테나치오": "catenaccio",
            "텐백": "park_the_bus",
            "폴스나인": "false_nine",
            "펄스나인": "false_nine",
            "프리미어리그": "premier_league",
            "premier league": "premier_league",
            "프리미어 리그": "premier_league",
            "라리가": "la_liga",
            "세리에": "serie_a",
            "index": "index"
        }
        target = page_map.get(page, page)
        if not re.match(r'^[a-z0-9_]+$', target):
            target = target.lower().replace(" ", "_")
            
        tool_calls.append({
            "tool": "read_wiki_page",
            "arguments": {"page_name": target}
        })
        res = mcp_server.read_wiki_page(target)
        if res.startswith("Error"):
            return prefix + f"MCP 도구 **read_wiki_page** 실행 실패 (대상: '{target}'): {res}"
        else:
            return prefix + f"에이전트가 MCP 도구 **read_wiki_page**로 위키 문서 '{target}'를 열었습니다:\n\n```markdown\n{res}\n```"
        
    # 4. Write/Add Wiki Page
    elif any(k in msg_lower for k in ["add", "write", "create", "추가", "작성", "생성", "써줘"]):
        title = "New Player/Tactic"
        tags = ["football"]
        links = ["/wiki/index.md"]
        content = "Detailed information."
        
        first_part = message.split(",")[0].split(":")[0]
        title = first_part
        for v in ["add", "write", "create", "추가", "작성", "생성", "player", "tactics", "club"]:
            title = re.sub(rf"\b{v}\b", "", title, flags=re.IGNORECASE).replace(v, "")
        title = title.strip()
        filename = title.lower().replace(" ", "_")
        
        if "호날두" in title or "ronaldo" in title.lower():
            filename = "cristiano_ronaldo"
            title = "Cristiano Ronaldo"
            tags = ["player", "forward", "al-nassr"]
        
        tags_match = re.search(r'(?:tags|태그):\s*([^,:\n]+)', message, re.IGNORECASE)
        if tags_match:
            tags = [t.strip() for t in tags_match.group(1).split()]
            
        content_match = re.search(r'(?:content|내용):\s*(.+)', message, re.IGNORECASE)
        if content_match:
            content = content_match.group(1).strip()
            
        tool_calls.append({
            "tool": "write_wiki_page",
            "arguments": {
                "page_name": filename,
                "title": title,
                "tags": tags,
                "links": links,
                "content": content
            }
        })
        res = mcp_server.write_wiki_page(filename, title, tags, links, content)
        return prefix + f"에이전트가 MCP 도구 **write_wiki_page**를 통해 새 지식을 추가했습니다:\n\n- **대상 문서**: `/wiki/{filename}.md`\n- **제목**: {title}\n- **결과**: {res}\n\n*대시보드를 확인하시면 카드 형태로 지식이 동적 추가된 것을 볼 수 있습니다!*"
    
    # 5. General Greeting/Conversation Fallback
    else:
        greeting_match = any(g in msg_lower for g in ["안녕", "반갑", "방가", "하이", "hello", "hi", "누구"])
        if greeting_match:
            return prefix + (
                "안녕하세요! 저는 축구 위키 관리 AI 에이전트(FootyAgent)입니다. ⚽\n\n"
                "로컬 모드에서는 자유로운 일상 대화가 제한되지만, 위키에 등록된 30개 축구 정보(손흥민, 메시, 게겐프레싱 등)에 대한 검색 및 조작 명령은 정상 실행됩니다.\n\n"
                "진짜 인공지능과 대화하듯 자유롭게 질문하고 위키를 자율적으로 관리하게 하려면, 잠시 후에 다시 요청하시거나 다른 구글 Gemini API Key를 `.env` 파일에 기입해 주세요!"
            )
        else:
            return prefix + (
                "현재 입력하신 일반 문장에 대한 실시간 AI 대화가 어렵습니다.\n\n"
                "Gemini API가 정상화되거나 새로운 API 키가 설정되면 실시간 AI 분석 및 자율 도구 실행이 가능해집니다.\n\n"
                "*사용 가능한 로컬 시뮬레이션 명령어 예시*:\n"
                "- **지식 검색**: `'손흥민 검색'`, `'Search tactics'`\n"
                "- **지식 읽기**: `'게겐프레싱 읽기'`, `'Read son_heung_min'`\n"
                "- **위키 건강 검사**: `'위키 검사'`, `'Check health'`\n"
                "- **새 문서 추가**: `'호날두 추가, 내용: 호날두는 포르투갈의 축구 전설입니다.'`"
            )

class FootballWikiHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Allow CORS for easy debugging
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.end_headers()

    def do_GET(self):
        # Route API: List all pages
        if self.path == "/api/pages":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            
            pages = []
            if os.path.exists(WIKI_DIR):
                for file in os.listdir(WIKI_DIR):
                    if file.endswith(".md"):
                        path = os.path.join(WIKI_DIR, file)
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                content = f.read()
                            # Normalize line endings to avoid CRLF issues on Windows
                            content = content.replace("\r\n", "\n")
                            # Parse metadata
                            title_match = re.search(r'title:\s*"(.*?)"', content)
                            title = title_match.group(1) if title_match else file.replace(".md", "")
                            
                            tags_match = re.search(r'tags:\s*\[(.*?)\]', content)
                            tags = [t.strip().strip('"').strip("'") for t in tags_match.group(1).split(",")] if tags_match else []
                            
                            links_match = re.search(r'links:\s*\[(.*?)\]', content)
                            links = [l.strip().strip('"').strip("'") for l in links_match.group(1).split(",")] if links_match else []
                            
                            version_match = re.search(r'version:\s*([0-9.]+)', content)
                            version = float(version_match.group(1)) if version_match else 1.0
                            
                            # Safely extract description by stripping headers, bolding, and links first
                            parts = content.split('---', 2)
                            body = parts[2].strip() if len(parts) >= 3 else content
                            
                            # Clean headers, HRs, links, and bold signs
                            clean_body = re.sub(r'^#+\s+.*$', '', body, flags=re.MULTILINE)
                            clean_body = re.sub(r'^---+$', '', clean_body, flags=re.MULTILINE)
                            clean_body = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', clean_body)
                            clean_body = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_body)
                            
                            lines = [l.strip() for l in clean_body.split('\n') if l.strip()]
                            first_p = lines[0] if lines else '상세 지식 정보가 위키 내에 기재되어 있습니다.'
                            desc = first_p[:150] + "..." if len(first_p) > 150 else first_p
                            
                            pages.append({
                                "filename": file,
                                "title": title,
                                "tags": tags,
                                "links": links,
                                "version": version,
                                "description": desc
                            })
                        except Exception as e:
                            pass
            self.wfile.write(json.dumps(pages, ensure_ascii=False).encode("utf-8"))
            return

        # Route API: Get single page content
        elif self.path.startswith("/api/pages/"):
            filename = self.path.replace("/api/pages/", "")
            path = os.path.join(WIKI_DIR, filename)
            if os.path.exists(path):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.wfile.write(f.read().encode("utf-8"))
                except Exception as e:
                    self.wfile.write(f"Error: {str(e)}".encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
            return

        # Route API: List all raw documents
        elif self.path == "/api/raw":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            
            raw_files = []
            if os.path.exists(RAW_DIR):
                for file in os.listdir(RAW_DIR):
                    if file.endswith(".txt") or file.endswith(".md"):
                        path = os.path.join(RAW_DIR, file)
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                content = f.read()
                            preview = content[:150] + "..." if len(content) > 150 else content
                            raw_files.append({
                                "filename": file,
                                "preview": preview
                            })
                        except Exception:
                            pass
            self.wfile.write(json.dumps(raw_files, ensure_ascii=False).encode("utf-8"))
            return

        # Route API: Get raw document content
        elif self.path.startswith("/api/raw/"):
            filename = self.path.replace("/api/raw/", "")
            path = os.path.join(RAW_DIR, filename)
            if os.path.exists(path) and os.path.isfile(path):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.wfile.write(f.read().encode("utf-8"))
                except Exception as e:
                    self.wfile.write(f"Error: {str(e)}".encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
            return

        # Route API: Get schema definition
        elif self.path == "/api/schema":
            if os.path.exists(SCHEMA_FILE):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                try:
                    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
                        self.wfile.write(f.read().encode("utf-8"))
                except Exception as e:
                    self.wfile.write(f"Error: {str(e)}".encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Schema file not found.")
            return

        # Serve static GUI files
        else:
            # Default to index.html if pointing to root
            if self.path == "/" or self.path == "":
                self.path = "/index.html"
            
            # Map path to gui/ directory
            requested_file = self.path.lstrip("/")
            full_path = os.path.join(GUI_DIR, requested_file)
            
            if os.path.exists(full_path) and os.path.isfile(full_path):
                self.send_response(200)
                # Content type mapping
                if requested_file.endswith(".html"):
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                elif requested_file.endswith(".css"):
                    self.send_header("Content-Type", "text/css; charset=utf-8")
                elif requested_file.endswith(".js"):
                    self.send_header("Content-Type", "application/javascript; charset=utf-8")
                self.end_headers()
                
                with open(full_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found.")
            return

    def do_POST(self):
        global chat_session, has_gemini
        if self.path == "/api/chat":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            req = json.loads(post_data.decode("utf-8"))
            message = req.get("message", "").strip()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            
            response_text = ""
            tool_calls = []
            
            try:
                if has_gemini and chat_session:
                    # Run conversation via Google Generative AI (Gemini 2.5 Flash)
                    response = chat_session.send_message(message)
                    response_text = response.text
                    
                    # Extract function call details from chat history
                    for turn in chat_session.history[-5:]:
                        for part in turn.parts:
                            if part.function_call:
                                tool_name = part.function_call.name
                                # Extract arguments safely
                                args = {}
                                for k, v in part.function_call.args.items():
                                    args[k] = list(v) if isinstance(v, (list, tuple)) else v
                                    
                                # Prevent duplicates in UI
                                if not any(tc["tool"] == tool_name and tc["arguments"] == args for tc in tool_calls):
                                    tool_calls.append({
                                        "tool": tool_name,
                                        "arguments": args
                                    })
                else:
                    # Fallback Mode: Rule-based local agent simulation
                    fallback_notice = "[⚠️ 로컬 시뮬레이션 모드 구동 중 - .env 파일에 GEMINI_API_KEY를 설정하여 실제 AI 모델을 활용하세요]\n\n"
                    response_text = run_local_fallback(message, tool_calls, fallback_notice)
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "quota" in err_msg.lower() or "limit" in err_msg.lower() or "exhausted" in err_msg.lower():
                    rate_limit_notice = (
                        "⚠️ **Gemini API 호출 제한(Rate Limit/Quota Exceeded)에 도달하여 임시 로컬 시뮬레이션 모드로 작동합니다.**\n"
                        "구글 제미나이 무료 API 플랜은 분당 요청 횟수(RPM) 제한이 있으며, 도구 실행 과정에서 여러 번 호출되어 초과되었습니다. "
                        "약 10초~1분 후에 다시 메세지를 전송하시면 실시간 AI 모드가 자동으로 재개됩니다.\n\n"
                    )
                    response_text = run_local_fallback(message, tool_calls, rate_limit_notice)
                else:
                    error_notice = (
                        f"⚠️ **Gemini API 실행 중 오류 발생 ({err_msg}). 임시 로컬 시뮬레이션 모드로 실행합니다.**\n\n"
                    )
                    response_text = run_local_fallback(message, tool_calls, error_notice)
                
            self.wfile.write(json.dumps({
                "response": response_text,
                "tool_calls": tool_calls
            }, ensure_ascii=False).encode("utf-8"))
            return

def run_server():
    os.makedirs(GUI_DIR, exist_ok=True)
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, FootballWikiHandler)
    print(f"Football Wiki Dashboard running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
