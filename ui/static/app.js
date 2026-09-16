document.addEventListener("DOMContentLoaded", () => {
    const md = window.markdownit({
        html: true,
        highlight: function (str, lang) {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return '<pre class="hljs"><code>' + hljs.highlight(str, { language: lang, ignoreIllegals: true }).value + '</code></pre>';
                } catch (__) {}
            }
            return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
        }
    });

    let currentAgentId = "chief-of-staff";
    let currentMode = "fun";
    let conversationMessages = [];
    let agentsList = [];

    // DOM Elements
    const chatContainer = document.getElementById("chat-container");
    const welcomeHero = document.getElementById("welcome-hero");
    const userInput = document.getElementById("user-input");
    const btnSend = document.getElementById("btn-send");
    const agentListContainer = document.getElementById("agent-list-container");
    const activeAgentName = document.getElementById("current-agent-name");
    const activeAgentAvatar = document.getElementById("current-agent-avatar");
    const activeAgentDesc = document.getElementById("current-agent-desc");
    const currentModeLabel = document.getElementById("current-mode-label");
    const btnNewChat = document.getElementById("btn-new-chat");

    // Mobile Sidebar Elements
    const sidebar = document.getElementById("sidebar");
    const sidebarBackdrop = document.getElementById("sidebar-backdrop");
    const btnSidebarToggle = document.getElementById("btn-sidebar-toggle");
    const btnSidebarClose = document.getElementById("btn-sidebar-close");

    function openMobileSidebar() {
        if (sidebar) sidebar.classList.add("open");
        if (sidebarBackdrop) sidebarBackdrop.classList.add("active");
    }

    function closeMobileSidebar() {
        if (sidebar) sidebar.classList.remove("open");
        if (sidebarBackdrop) sidebarBackdrop.classList.remove("active");
    }

    if (btnSidebarToggle) btnSidebarToggle.addEventListener("click", openMobileSidebar);
    if (btnSidebarClose) btnSidebarClose.addEventListener("click", closeMobileSidebar);
    if (sidebarBackdrop) sidebarBackdrop.addEventListener("click", closeMobileSidebar);

    // Modal Elements
    const modalCreateAgent = document.getElementById("modal-create-agent");
    const btnOpenCreateAgent = document.getElementById("btn-open-create-agent");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const btnCancelModal = document.getElementById("btn-cancel-modal");
    const formCreateAgent = document.getElementById("form-create-agent");

    // Load Agents
    function fetchAgents() {
        fetch("/api/agents")
            .then(res => res.json())
            .then(data => {
                agentsList = data;
                const defaultAgent = agentsList.find(a => a.id === currentAgentId) || agentsList[0];
                if (defaultAgent) {
                    selectAgent(defaultAgent);
                } else {
                    renderAgentList();
                }
            })
            .catch(err => console.error("Error loading agents:", err));
    }

    function renderAgentList() {
        agentListContainer.innerHTML = "";
        agentsList.forEach(agent => {
            const card = document.createElement("div");
            card.className = `agent-card ${agent.id === currentAgentId ? "active" : ""}`;
            card.innerHTML = `
                <span class="agent-card-avatar">${agent.avatar}</span>
                <div class="agent-card-info">
                    <h4>${agent.name}</h4>
                    <p>${agent.description}</p>
                </div>
            `;
            card.addEventListener("click", () => selectAgent(agent));
            agentListContainer.appendChild(card);
        });
    }

    function selectAgent(agent) {
        currentAgentId = agent.id;
        activeAgentName.textContent = agent.name;
        activeAgentAvatar.textContent = agent.avatar;
        activeAgentDesc.textContent = agent.description;
        renderAgentList();
        if (window.innerWidth <= 768) {
            closeMobileSidebar();
        }
    }

    // Mode Selector
    document.querySelectorAll(".mode-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentMode = btn.dataset.mode;
            
            const modeLabels = {
                fun: '<i class="fa-solid fa-masks-theater"></i> Fun Mode Active',
                regular: '<i class="fa-solid fa-bolt"></i> Regular Mode Active',
                think: '<i class="fa-solid fa-brain"></i> Think Mode Active'
            };
            currentModeLabel.innerHTML = modeLabels[currentMode];
        });
    });

    // Quick Cards
    document.querySelectorAll(".quick-card").forEach(card => {
        card.addEventListener("click", () => {
            userInput.value = card.dataset.prompt;
            sendMessage();
        });
    });

    // Modal Control
    btnOpenCreateAgent.addEventListener("click", () => modalCreateAgent.classList.add("open"));
    btnCloseModal.addEventListener("click", () => modalCreateAgent.classList.remove("open"));
    btnCancelModal.addEventListener("click", () => modalCreateAgent.classList.remove("open"));

    formCreateAgent.addEventListener("submit", (e) => {
        e.preventDefault();
        const selectedTools = Array.from(document.querySelectorAll("input[name='tools']:checked")).map(cb => cb.value);
        
        const payload = {
            name: document.getElementById("agent-name").value,
            avatar: document.getElementById("agent-avatar").value || "🤖",
            description: document.getElementById("agent-desc").value,
            system_prompt: document.getElementById("agent-prompt").value,
            tools: selectedTools,
            temperature: 0.7
        };

        fetch("/api/agents", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(newAgent => {
            modalCreateAgent.classList.remove("open");
            formCreateAgent.reset();
            fetchAgents();
            selectAgent(newAgent);
        });
    });

    // New Chat
    btnNewChat.addEventListener("click", () => {
        conversationMessages = [];
        chatContainer.innerHTML = "";
        chatContainer.appendChild(welcomeHero);
        if (window.innerWidth <= 768) {
            closeMobileSidebar();
        }
    });

    // Send Message
    function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        if (welcomeHero && welcomeHero.parentNode) {
            welcomeHero.parentNode.removeChild(welcomeHero);
        }

        // Render User Message
        appendMessage("user", text);
        conversationMessages.push({ role: "user", content: text });
        userInput.value = "";

        // Prepare Assistant Shell
        const assistantMsgDiv = appendMessage("assistant", "");
        const bodyDiv = assistantMsgDiv.querySelector(".chat-msg-body");

        // SSE Request
        fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                messages: conversationMessages,
                agent_id: currentAgentId,
                mode: currentMode
            })
        })
        .then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedContent = "";

            function readChunk() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        conversationMessages.push({ role: "assistant", content: accumulatedContent });
                        return;
                    }
                    const chunk = decoder.decode(value);
                    const lines = chunk.split("\n\n");
                    
                    lines.forEach(line => {
                        if (line.startsWith("data: ")) {
                            try {
                                const event = JSON.parse(line.replace("data: ", ""));
                                handleChatEvent(event, bodyDiv, (text) => { accumulatedContent += text; });
                            } catch (e) {}
                        }
                    });
                    readChunk();
                });
            }
            readChunk();
        });
    }

    function handleChatEvent(event, bodyDiv, onContent) {
        if (event.type === "content") {
            onContent(event.content);
            bodyDiv.innerHTML = md.render(event.content);
        } else if (event.type === "warning" || event.type === "error") {
            const alertCard = document.createElement("div");
            alertCard.className = "tool-card";
            const isErr = event.type === "error";
            alertCard.style.borderColor = isErr ? "#ef4444" : "#f59e0b";
            alertCard.style.background = isErr ? "rgba(239, 68, 68, 0.1)" : "rgba(245, 158, 11, 0.1)";
            alertCard.innerHTML = `
                <div class="tool-card-header" style="color: ${isErr ? '#ef4444' : '#f59e0b'};">
                    <i class="fa-solid fa-triangle-exclamation"></i> ${isErr ? 'Gateway Error' : 'Gateway Warning'}
                </div>
                <div class="tool-card-body" style="font-size: 0.85rem; color: #cbd5e1;">${event.content}</div>
            `;
            bodyDiv.appendChild(alertCard);
        } else if (event.type === "delegation_call") {
            const delegationCard = document.createElement("div");
            delegationCard.className = "tool-card delegation-card";
            delegationCard.style.borderColor = "var(--accent-amber)";
            delegationCard.innerHTML = `
                <div class="tool-card-header" style="color: var(--accent-amber);">
                    <i class="fa-solid fa-crown"></i> Chief of Staff Delegating to: <strong>${event.staff_agent_id}</strong>
                </div>
                <div class="tool-card-body">Instruction: ${event.instruction}</div>
            `;
            bodyDiv.appendChild(delegationCard);
        } else if (event.type === "tool_call") {
            const toolCard = document.createElement("div");
            toolCard.className = "tool-card";
            toolCard.innerHTML = `
                <div class="tool-card-header">
                    <i class="fa-solid fa-gear fa-spin"></i> Executing Tool: ${event.tool_name}
                </div>
                <div class="tool-card-body">Arguments: ${JSON.stringify(event.arguments, null, 2)}</div>
            `;
            bodyDiv.appendChild(toolCard);
        } else if (event.type === "tool_result") {
            const lastToolCard = bodyDiv.querySelector(".tool-card:last-child");
            if (lastToolCard) {
                lastToolCard.querySelector(".tool-card-header").innerHTML = `<i class="fa-solid fa-circle-check"></i> Tool Completed: ${event.tool_name}`;
            }
        }
    }


    function appendMessage(role, content) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `chat-msg ${role}`;
        
        const avatar = role === "user" ? '<i class="fa-solid fa-user"></i>' : (activeAgentAvatar.textContent || "🤖");
        
        msgDiv.innerHTML = `
            <div class="chat-msg-avatar">${avatar}</div>
            <div class="chat-msg-body">${md.render(content)}</div>
        `;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return msgDiv;
    }

    btnSend.addEventListener("click", sendMessage);
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Load Pod Status & Sessions
    function fetchPodStatus() {
        fetch("/api/pod/status")
            .then(res => res.json())
            .then(data => {
                const titleEl = document.getElementById("pod-server-title");
                const subEl = document.getElementById("pod-server-sub");
                const dotEl = document.getElementById("pod-status-dot");
                if (data.online) {
                    if (titleEl) titleEl.textContent = `Hermes Pod (${data.model})`;
                    if (subEl) subEl.textContent = `🟢 ONLINE • ${data.skills_count} Skills`;
                    if (dotEl) dotEl.className = "status-dot online";
                } else {
                    if (subEl) subEl.textContent = "🔴 Offline / Disconnected";
                    if (dotEl) dotEl.className = "status-dot offline";
                }
            })
            .catch(err => console.error("Error fetching Pod status:", err));
    }

    function fetchPodSessions() {
        fetch("/api/pod/sessions")
            .then(res => res.json())
            .then(sessions => {
                const historyList = document.getElementById("history-list");
                if (!historyList) return;
                historyList.innerHTML = "";

                if (!sessions || sessions.length === 0) {
                    historyList.innerHTML = '<div class="history-item">No sessions recorded</div>';
                    return;
                }

                sessions.forEach(sess => {
                    const item = document.createElement("div");
                    item.className = "history-item";
                    const title = sess.title || sess.preview || `Session ${sess.id}`;
                    item.innerHTML = `<i class="fa-regular fa-message"></i> <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 170px;">${title}</span>`;
                    item.addEventListener("click", () => loadPodSession(sess.id, item));
                    historyList.appendChild(item);
                });
            })
            .catch(err => console.error("Error fetching Pod sessions:", err));
    }

    function loadPodSession(sessionId, clickedElement) {
        document.querySelectorAll(".history-item").forEach(el => el.classList.remove("active"));
        if (clickedElement) clickedElement.classList.add("active");

        fetch(`/api/pod/sessions/${sessionId}/messages`)
            .then(res => res.json())
            .then(messages => {
                chatContainer.innerHTML = "";
                conversationMessages = [];

                if (!messages || messages.length === 0) {
                    chatContainer.innerHTML = '<div style="padding: 20px; color: var(--text-secondary);">No messages in this session.</div>';
                    return;
                }

                messages.forEach(msg => {
                    if (msg.role === "user" || msg.role === "assistant") {
                        appendMessage(msg.role, msg.content || "");
                        conversationMessages.push({ role: msg.role, content: msg.content || "" });
                    }
                });

                if (window.innerWidth <= 768) {
                    closeMobileSidebar();
                }
            })
            .catch(err => console.error("Error loading session messages:", err));
    }

    fetchAgents();
    fetchPodStatus();
    fetchPodSessions();
});

