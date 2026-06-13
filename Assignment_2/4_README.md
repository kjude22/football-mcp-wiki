# ⚽ Football Tactics & Player Wiki (MCP Server & GUI Tool)

본 프로젝트는 **Andrej Karpathy의 LLM Wiki 패러다임**을 기반으로 설계된, 현대 축구 전술 및 선수 데이터를 다루는 사전 컴파일 지식 저장소 시스템입니다. **MCP (Model Context Protocol)** 기술과 **Google Gemini API**의 **Function Calling (기능 호출)** 기능을 결합하여, 실제 AI 모델이 위키 데이터를 직접 조작하고 감증하는 자율형 에이전트 인터페이스를 구동합니다.

---

## 1. 프로젝트 설계 철학 및 AI 에이전트의 역할 (Why & Design)
*   **지식 코드베이스 관리자**: AI 챗봇은 단순 잡담 상대가 아니라, 위키 폴더(`wiki/`)를 지속 가능한 소프트웨어 코드베이스처럼 관리하는 **위키 프로그래머 에이전트(FootyAgent)**입니다.
*   **자율 도구 사용 (Gemini Function Calling)**: 사용자가 자연어로 입력하면, Gemini 모델이 본문의 의도를 파악하여 제공된 MCP 도구(`search_wiki`, `read_wiki_page`, `write_wiki_page`, `verify_wiki_health`)를 직접 자율 선택하여 구동합니다.
*   **30개의 상호 연결 지식망**: 12명의 대표 선수, 10개의 유명 클럽, 5가지 주요 전술, 3개 리그 등 총 30개의 상호 의존적 파일 데이터베이스를 구축하여 지식 관계망 시각화 효과를 극대화했습니다.

---

## 2. 제공하는 MCP Tool 명세
`mcp_server.py`는 AI 에이전트의 호출을 위해 아래 4가지 핵심 도구를 노출하고 있습니다.

1.  **`search_wiki(query: str) -> str`**
    *   *기능*: 위키 내 모든 지식의 파일명과 마크다운 본문을 대상으로 가중치 기반 다차원 키워드 검색을 실행하여 관련 노드를 추천합니다.
2.  **`read_wiki_page(page_name: str) -> str`**
    *   *기능*: 특정 파일명의 지식 페이지를 열어 YAML frontmatter 메타데이터와 마크다운 본문을 있는 그대로 반환합니다.
3.  **`write_wiki_page(page_name: str, title: str, tags: list[str], links: list[str], content: str) -> str`**
    *   *기능*: 일관성 있는 YAML 메타데이터 스키마(제목, 태그, 업데이트일, 링크 리스트)를 적용하여 신규 축구 문서를 생성하거나 기존 문서를 수정하며 버전을 0.1씩 자동으로 증분합니다.
4.  **`verify_wiki_health() -> str`**
    *   *기능*: 위키 저장소의 무결성을 전수 스캔하여 잘못된 스키마, 깨진 내부 상대 경로, 다른 파일이 가리키지 않는 고아(Orphan) 문서를 식별해 내고 종합 건강도(Health Score) 점수를 산출합니다.

---

## 3. 프로젝트 디렉토리 구조 (Directory Structure)

*   `harness/`: 에이전트 가이드라인 및 구문/참조 무결성 검증 영역
    *   `harness/RULES.md`: 에이전트의 권한 제한 및 안전 작동 지침
    *   `harness/skills/audit_syntax.py`: 위키 전체 무결성을 로컬 검증하는 스크립트 (**SKILL**)
*   `raw/`: 에이전트가 위키로 변환하기 전의 소스 미가공 텍스트
    *   `raw/new_player_sample.txt`: 신규 등록 및 컴파일 테스트용 샘플 원본 텍스트
*   `schema/`: 위키 지식 메타데이터 형식 표준
    *   `schema/schema.md`: YAML 헤더 및 마크다운 포맷 스키마 명세서
*   `tools/`: MCP API 도구와 웹 대시보드 백엔드 코드
    *   `tools/mcp_server.py`: FastMCP 프레임워크 기반의 도구 구현체
    *   `tools/server.py`: 웹 대시보드 코디네이터 서버
*   `gui/`: 대시보드 프론트엔드 코드 (HTML, CSS, JS)
*   `wiki/`: 에이전트가 사전 컴파일하여 교차 적재한 30종의 위키 지식 문서
*   `demo/`: 프로그램 실행 시각화 캡처 스크린샷 (`demo/screenshot.png`)

---

## 4. 실행 환경 및 의존성 (Environment & Setup)

### 4.1 최소 환경 사양
*   **OS**: Windows 10/11 이상
*   **Python**: Python 3.10 이상

### 4.2 패키지 의존성 설치
본 프로젝트는 시스템의 가벼움과 안정성을 극대화하기 위해 파이썬 표준 라이브러리 위주로 개발되었으며, MCP 및 Gemini SDK 구동을 위한 공식 패키지만 설치해 주시면 됩니다.
```bash
pip install mcp google-generativeai python-dotenv pyyaml
```

### 4.3 Gemini API Key 설정 (보안)
AI 에이전트가 실제 인공지능 모델을 사용해 작동하게 하려면, 프로젝트 루트 폴더에 생성된 `.env` 파일에 API 키를 등록합니다.
```env
# .env 파일 편집 (주의: 깃허브 업로드 대상에서 제외됨)
GEMINI_API_KEY="AI_모델_구동을_위한_제미나이_API_키_기입"
```
*(만약 API 키가 누락되었을 경우, 자동으로 **로컬 에이전트 시뮬레이션 모드**로 안전하게 폴백되어 작동하므로 오류로 중단되지 않습니다.)*

---

## 5. 작동 방법 및 테스트 가이드

### 5.1 대시보드 및 서버 실행
프로젝트 루트 디렉토리에서 아래 명령을 실행하면, 경량 웹 서빙 코디네이터가 구동됩니다.
```bash
python tools/server.py
```
*   콘솔창에 `Football Wiki Dashboard running at http://localhost:8000` 로그가 나타납니다.
*   크롬 등 브라우저를 열고 `http://localhost:8000` 주소로 접속하면 프리미엄 카드 대시보드가 시작됩니다.

### 5.2 주요 테스트 시나리오
1.  **30개 지식 카드 탐색 및 관계망 네비게이션**:
    *   대시보드에서 30개 지식 카드가 로드됩니다. 카드를 클릭하여 상세 페이지 모달을 열고 하단의 꼬리 링크(Connection Buttons)를 타고 다른 카드들로 즉시 이동하는 관계망을 탐색합니다.
2.  **Raw 원본 문서 및 Schema 명세 탐색**:
    *   대시보드 왼쪽 사이드바의 **`📄 원본 문서 (Raw)`** 탭을 클릭하여 `raw/` 디렉토리에 위치한 원본 소스 문서들의 목록과 원문을 탐색합니다.
    *   사이드바의 **`📐 위키 스키마 (Schema)`** 탭을 클릭하여 위키가 준수하는 메타데이터 명세를 대시보드 상에서 직접 확인합니다.
3.  **실시간 위키 건강도 검사**:
    *   우측 상단 Scorecard의 `실시간 감사 실행` 버튼을 누르거나, 챗봇에 `"위키 상태 점검해줘"` 또는 `"verify health"`를 전송합니다.
    *   에이전트가 `verify_wiki_health` 도구를 실행해 100% 점수를 반환하는 로그가 노출됩니다. 또는 로컬 터미널에서 직접 `python harness/skills/audit_syntax.py`를 실행하여 정밀 진단할 수도 있습니다.
4.  **실제 AI 모델을 이용한 지식 자동 적재 및 업데이트**:
    *   챗봇 하단 입력창에 자유로운 자연어로 명령합니다:
        > `"독일에 있는 바이에른 뮌헨 클럽 정보를 읽어오고 해리 케인 선수와 연동해서 위키에 추가해줘"`
    *   Gemini 모델이 직접 `read_wiki_page`, `write_wiki_page` 도구를 차례로 적법하게 판단하여 실행하고 결과를 리포트합니다.
    *   지식이 새로 작성되는 순간 대시보드 좌측 카드 레이아웃에 새 카드가 비동기 동적 생성되는 것을 실시간으로 관찰할 수 있습니다.

---

## 6. [⏱️ 30분 초고속 가이드] 나만의 자료 1건으로 첫 위키 페이지 만들고 확인하기

본 프로젝트에 처음 접속한 사용자가 30분 이내에 자신의 개별 자료를 투입하여 새 지식 카드를 빌드하는 과정입니다.

1.  **미가공 데이터 투입 (Data Input):**
    *   텍스트 편집기나 메모장을 열어 새 선수 정보나 전술 노트를 작성합니다.
    *   해당 파일명은 영문 snake_case로 규정하여 `raw/` 폴더에 저장합니다. (예: `raw/cristiano_ronaldo.txt`)
2.  **서버 구동:**
    *   터미널에서 `python tools/server.py`를 실행하고 브라우저로 `http://localhost:8000`에 접속합니다.
    *   좌측 메뉴의 **`📄 원본 문서 (Raw)`** 탭에 방금 생성한 `cristiano_ronaldo.txt` 문서가 리스트업된 것을 확인합니다.
3.  **에이전트에 통합 요청 (Integration Request):**
    *   우측 챗봇 입력창에 다음과 같이 자연어로 요청합니다:
        > `"raw/cristiano_ronaldo.txt 원본 파일 내용을 읽고, 관련 태그들을 추출하여 위키에 새 문서로 작성해줘. 연동할 링크는 /wiki/real_madrid.md 와 /wiki/premier_league.md 로 등록해줘."`
    *   에이전트가 `read_wiki_page`, `write_wiki_page` 도구를 자율적으로 파라미터를 계산하여 실행하고 결과를 답변합니다.
4.  **검증 및 화면 확인 (Validation & Screen Check):**
    *   대시보드의 **`📚 전체 지식`** 탭으로 돌아옵니다.
    *   대시보드 상에 **`Cristiano Ronaldo`** 이름의 신규 지식 카드가 비동기식으로 실시간 렌더링되어 추가된 것을 눈으로 확인합니다!
    *   우측 상단의 `실시간 감사 실행` 버튼을 눌러, 추가된 문서로 인해 깨진 내부 참조 링크가 발생하지 않았는지 무결성을 즉시 검증합니다.
