let allPages = [];
let currentFilter = 'all';

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
    fetchPages();
    auditWiki(); // Get initial health score
});

// Fetch all pages from API
async function fetchPages() {
    try {
        const res = await fetch("/api/pages");
        if (res.ok) {
            allPages = await res.json();
            renderCards();
        }
    } catch (e) {
        console.error("Error fetching pages:", e);
    }
}


// Render Wiki Cards in Grid
function renderCards() {
    const grid = document.getElementById("cardsGrid");
    grid.innerHTML = "";
    
    const filtered = allPages.filter(p => {
        if (currentFilter === 'all') return p.filename !== 'index.md';
        
        // Match filter with tags
        return p.tags.includes(currentFilter);
    });
    
    if (filtered.length === 0) {
        grid.innerHTML = '<div class="loading-state">검색된 지식이 없습니다.</div>';
        return;
    }
    
    filtered.forEach(p => {
        // Find primary tag for styling
        let type = 'player';
        if (p.tags.includes('club')) type = 'club';
        else if (p.tags.includes('tactics')) type = 'tactics';
        else if (p.tags.includes('league')) type = 'league';
        
        const card = document.createElement("div");
        card.className = "wiki-card";
        card.onclick = () => openPage(p.filename);
        
        // Map related pages into names for preview tags
        const relations = p.links.map(link => {
            const base = link.replace("/wiki/", "").replace(".md", "");
            return base.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
        });
        
        card.innerHTML = `
            <div class="card-header">
                <span class="tag ${type}">${type}</span>
                <span class="card-ver">v${p.version.toFixed(1)}</span>
            </div>
            <h3>${p.title}</h3>
            <p>${p.description}</p>
            <div class="card-relations">
                ${relations.map(r => `<span class="rel-tag">🔗 ${r}</span>`).join("")}
            </div>
        `;
        grid.appendChild(card);
    });
}

// Filter Cards from Sidebar
function filterWiki(type) {
    switchView('wiki');
    currentFilter = type;
    document.querySelectorAll(".nav-links a").forEach(a => a.classList.remove("active"));
    
    let btnId = "btnWikiAll";
    if (type === 'player') btnId = "btnWikiPlayer";
    else if (type === 'club') btnId = "btnWikiClub";
    else if (type === 'tactics') btnId = "btnWikiTactics";
    document.getElementById(btnId).classList.add("active");
    
    renderCards();
}

// Open Detail Page Modal
async function openPage(filename) {
    try {
        const res = await fetch(`/api/pages/${filename}`);
        if (res.ok) {
            const rawContent = await res.text();
            showModal(filename, rawContent);
        }
    } catch (e) {
        console.error("Error opening page:", e);
    }
}

// Custom simple markdown parser
function parseMarkdown(md) {
    // Strip frontmatter
    let body = md;
    if (md.startsWith("---")) {
        const parts = md.split("---");
        body = parts.slice(2).join("---").trim();
    }
    
    // Parse headers
    body = body.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
    body = body.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
    body = body.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
    
    // Parse bold
    body = body.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Parse custom relative markdown links: [Text](/wiki/target.md)
    // Map them to js actions inside modal
    body = body.replace(/\[(.*?)\]\(\/wiki\/(.*?)\)/g, (match, text, target) => {
        return `<a href="#" onclick="event.preventDefault(); openPage('${target}')">${text}</a>`;
    });
    
    // Parse line breaks
    body = body.replace(/\n/g, '<br>');
    
    return body;
}

// Show Modal
function showModal(filename, content) {
    const page = allPages.find(p => p.filename === filename) || { title: "Details", tags: ["football"], links: [] };
    
    // Set tag badge
    let type = 'player';
    if (page.tags.includes('club')) type = 'club';
    else if (page.tags.includes('tactics')) type = 'tactics';
    else if (page.tags.includes('league')) type = 'league';
    
    document.getElementById("modalTag").className = `tag ${type}`;
    document.getElementById("modalTag").textContent = type;
    
    // Parse and set content
    const htmlBody = parseMarkdown(content);
    document.getElementById("modalBody").innerHTML = htmlBody;
    
    // Set connections list
    const connectionsContainer = document.getElementById("modalConnections");
    connectionsContainer.innerHTML = "";
    
    if (page.links.length === 0) {
        connectionsContainer.innerHTML = "<span style='font-size:11px;color:gray;'>연결된 지식이 없습니다.</span>";
    } else {
        page.links.forEach(link => {
            const targetFilename = link.replace("/wiki/", "");
            if (targetFilename === "index.md") return; // Skip link back to home
            
            const targetTitle = targetFilename.replace(".md", "").replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
            
            const btn = document.createElement("button");
            btn.className = "connection-link-btn";
            btn.textContent = `🔗 ${targetTitle}`;
            btn.onclick = () => {
                openPage(targetFilename);
            };
            connectionsContainer.appendChild(btn);
        });
    }
    
    document.getElementById("detailModal").classList.add("active");
}

function closeModal() {
    document.getElementById("detailModal").classList.remove("active");
}

// Trigger Health Audit via Agent call
async function auditWiki() {
    const healthValue = document.getElementById("healthValue");
    const healthStats = document.getElementById("healthStats");
    
    healthValue.textContent = "--%";
    healthStats.textContent = "감사 준비 중...";
    
    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: "verify health" })
        });
        if (res.ok) {
            const data = await res.json();
            
            // Extract health score using regex from response text
            const scoreMatch = data.response.match(/Health Score:\s*(\d+)%/);
            const score = scoreMatch ? scoreMatch[1] : 100;
            
            const filesMatch = data.response.match(/Total Files Audited:\s*(\d+)/);
            const files = filesMatch ? filesMatch[1] : 0;
            
            const brokenMatch = data.response.match(/Broken Links:\s*(\d+)/);
            const broken = brokenMatch ? brokenMatch[1] : 0;
            
            // Update UI Ring color based on score
            const ring = document.querySelector(".health-score-ring");
            ring.style.background = `conic-gradient(var(--primary) ${score}%, var(--border-color) 0)`;
            
            healthValue.textContent = `${score}%`;
            healthStats.textContent = `총 파일 ${files}개 | 깨진 링크 ${broken}개`;
        }
    } catch (e) {
        healthValue.textContent = "Error";
        healthStats.textContent = "연결 실패";
    }
}

// Handle Chat Message Submit
async function handleChatSubmit(e) {
    if (e) e.preventDefault();
    const input = document.getElementById("chatInput");
    const message = input.value.trim();
    if (!message) return;
    
    // Add User Message
    addChatMessage(message, "user");
    input.value = "";
    
    // Activate tool calling animation
    const toolIndicator = document.getElementById("toolCallIndicator");
    const toolName = document.getElementById("toolName");
    toolIndicator.style.display = "flex";
    
    // Determine simulated tool call name for visual premium feel
    let expectedTool = "search_wiki";
    if (message.toLowerCase().includes("health") || message.toLowerCase().includes("check")) expectedTool = "verify_wiki_health";
    else if (message.toLowerCase().includes("read") || message.toLowerCase().includes("get")) expectedTool = "read_wiki_page";
    else if (message.toLowerCase().includes("add") || message.toLowerCase().includes("write")) expectedTool = "write_wiki_page";
    toolName.textContent = expectedTool;
    
    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        });
        
        toolIndicator.style.display = "none";
        
        if (res.ok) {
            const data = await res.json();
            
            // Render Agent Response
            addChatMessage(data.response, "agent", data.tool_calls);
            
            // If page was written, refetch
            if (data.tool_calls && data.tool_calls.some(tc => tc.tool === "write_wiki_page")) {
                fetchPages();
                auditWiki();
            }
        } else {
            addChatMessage("에이전트 통신 오류가 발생했습니다.", "agent");
        }
    } catch (e) {
        toolIndicator.style.display = "none";
        addChatMessage("서버에 연결할 수 없습니다.", "agent");
    }
}

// Preset suggestions helper
function sendSuggested(text) {
    document.getElementById("chatInput").value = text;
    handleChatSubmit();
}

// Append message block to history panel
function addChatMessage(text, sender, toolCalls = []) {
    const history = document.getElementById("chatHistory");
    const msg = document.createElement("div");
    msg.className = `chat-message ${sender}`;
    
    let htmlContent = "";
    
    // If agent executed tools, display badge
    if (toolCalls && toolCalls.length > 0) {
        toolCalls.forEach(tc => {
            htmlContent += `<div class="tool-badge">Invoked Tool: ${tc.tool}(${JSON.stringify(tc.arguments)})</div>`;
        });
    }
    
    // Render text with simple line breaks or markdown formatting
    let formattedText = text
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/`(.*?)`/g, "<code>$1</code>");
        
    htmlContent += `<div>${formattedText}</div>`;
    
    msg.innerHTML = htmlContent;
    history.appendChild(msg);
    history.scrollTop = history.scrollHeight;
}

// Switch Dashboard Views (Wiki / Raw / Schema)
function switchView(viewName) {
    const wikiView = document.getElementById("wikiView");
    const rawView = document.getElementById("rawView");
    const schemaView = document.getElementById("schemaView");
    
    // Hide all
    wikiView.style.display = "none";
    rawView.style.display = "none";
    schemaView.style.display = "none";
    
    // Remove active styles from sidebar nav links
    document.querySelectorAll(".nav-links a").forEach(a => a.classList.remove("active"));
    
    if (viewName === 'wiki') {
        wikiView.style.display = "block";
    } else if (viewName === 'raw') {
        rawView.style.display = "block";
        document.getElementById("btnRawTab").classList.add("active");
        fetchRawDocuments();
    } else if (viewName === 'schema') {
        schemaView.style.display = "block";
        document.getElementById("btnSchemaTab").classList.add("active");
        fetchSchema();
    }
}

// Fetch list of raw source files
async function fetchRawDocuments() {
    const rawList = document.getElementById("rawList");
    rawList.innerHTML = '<div style="color:gray;font-size:12px;padding:20px;text-align:center;">불러오는 중...</div>';
    
    try {
        const res = await fetch("/api/raw");
        if (res.ok) {
            const files = await res.json();
            rawList.innerHTML = "";
            
            if (files.length === 0) {
                rawList.innerHTML = '<div style="color:gray;font-size:12px;padding:20px;text-align:center;">raw/ 폴더에 원본 문서가 없습니다.</div>';
                return;
            }
            
            files.forEach(file => {
                const item = document.createElement("div");
                item.className = "raw-item";
                item.onclick = () => {
                    document.querySelectorAll(".raw-item").forEach(el => el.classList.remove("active"));
                    item.classList.add("active");
                    openRawDocument(file.filename);
                };
                item.innerHTML = `
                    <h4>📄 ${file.filename}</h4>
                    <p>${file.preview}</p>
                `;
                rawList.appendChild(item);
            });
        }
    } catch (e) {
        console.error("Error fetching raw files:", e);
        rawList.innerHTML = '<div style="color:red;font-size:12px;padding:20px;text-align:center;">불러오기 실패</div>';
    }
}

// Fetch single raw source document content
async function openRawDocument(filename) {
    const preview = document.getElementById("rawPreview");
    preview.textContent = "불러오는 중...";
    
    try {
        const res = await fetch(`/api/raw/${filename}`);
        if (res.ok) {
            const content = await res.text();
            preview.textContent = content;
        } else {
            preview.textContent = "파일을 읽는 도중 오류가 발생했습니다.";
        }
    } catch (e) {
        console.error("Error reading raw file:", e);
        preview.textContent = "서버 연결에 실패했습니다.";
    }
}

// Fetch and render schema markdown content
async function fetchSchema() {
    const container = document.getElementById("schemaContainer");
    container.innerHTML = '<div style="color:gray;font-size:12px;padding:20px;text-align:center;">불러오는 중...</div>';
    
    try {
        const res = await fetch("/api/schema");
        if (res.ok) {
            const md = await res.text();
            container.innerHTML = parseMarkdownToHtml(md);
        } else {
            container.innerHTML = '<div style="color:red;font-size:12px;padding:20px;text-align:center;">스키마 파일이 존재하지 않습니다.</div>';
        }
    } catch (e) {
        console.error("Error fetching schema:", e);
        container.innerHTML = '<div style="color:red;font-size:12px;padding:20px;text-align:center;">서버 연결 실패</div>';
    }
}

// Basic markdown to html helper (handles tables, paragraphs, lists, headers)
function parseMarkdownToHtml(md) {
    let html = md;
    
    // Normalize line endings
    html = html.replace(/\r\n/g, "\n");
    
    // Strip frontmatter if any
    if (html.startsWith("---")) {
        const parts = html.split("---");
        html = parts.slice(2).join("---").trim();
    }
    
    // Parse tables
    html = html.replace(/^\|(.*?)\|$/gm, (match, row) => {
        const cols = row.split("|").map(c => c.trim());
        if (cols.every(c => c.startsWith(":") || c.startsWith("-"))) {
            return ""; // Skip divider rows
        }
        return `<tr>${cols.map(c => `<td>${c}</td>`).join("")}</tr>`;
    });
    // Wrap consecutive tr elements with table
    html = html.replace(/(<tr>.*?<\/tr>)+/gs, (match) => {
        let processed = match;
        if (processed.includes("<tr>")) {
            processed = processed.replace("<tr>", "<thead><tr>").replace("</tr>", "</tr></thead><tbody>") + "</tbody>";
            processed = processed.replace(/<td>/g, "<th>").replace(/<\/td>/g, "</th>");
            const parts = processed.split("</thead><tbody>");
            if (parts.length > 1) {
                parts[1] = parts[1].replace(/<th>/g, "<td>").replace(/<\/th>/g, "<\/td>");
                processed = parts.join("</thead><tbody>");
            }
        }
        return `<table>${processed}</table>`;
    });
    
    // Parse headers
    html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
    html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
    html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
    
    // Parse lists
    html = html.replace(/^\-\s+(.*?)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*?<\/li>)+/gs, '<ul>$&</ul>');
    
    // Parse bold & code block
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Parse pre code blocks
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="$1">$2</code></pre>');
    
    // Parse links
    html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // Parse paragraphs
    const lines = html.split("\n");
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line && !line.startsWith("<") && !line.startsWith("---")) {
            lines[i] = `<p>${line}</p>`;
        }
    }
    html = lines.join("\n");
    
    return html;
}
