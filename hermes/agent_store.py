import os
import json
import uuid

AGENTS_FILE = os.path.join(os.path.dirname(__file__), "..", "agents_data.json")

DEFAULT_AGENTS = [
    {
        "id": "chief-of-staff",
        "name": "Chief of Staff 👑",
        "avatar": "👑",
        "description": "Leader Manager Agent that orchestrates and delegates sub-tasks to specialized Staff Agents.",
        "system_prompt": (
            "You are the Chief of Staff Agent, the executive leader and manager of the Grok AI Multi-Agent System. "
            "Your role is to orchestrate complex user requests by breaking them down into clear sub-tasks, "
            "delegating tasks to specialized Staff Agents using the <tool_call>{\"name\": \"delegate_to_staff\", \"arguments\": {\"staff_agent_id\": \"...\", \"subtask_instruction\": \"...\"}}</tool_call> tool, "
            "evaluating their staff responses, and synthesizing a comprehensive executive summary for the user."
        ),
        "tools": ["delegate_to_staff", "sumopod_get_pod_status", "sumopod_list_remote_skills", "sumopod_trigger_webhook", "gdrive_list_files", "gdrive_read_file", "gdrive_upload_file", "web_search", "execute_python", "fetch_web_page", "get_system_time"],
        "temperature": 0.5,
        "is_default": True
    },
    {
        "id": "grok-original",
        "name": "Grok Original",
        "avatar": "🤖",
        "description": "Iconic witty, direct, highly intelligent, and unfiltered Grok AI.",
        "system_prompt": (
            "You are Grok, an AI modeled after the Hitchhiker's Guide to the Galaxy. "
            "You are witty, highly intelligent, direct, rebellious, and humorous with a touch of sarcasm. "
            "You answer questions with candor and sharp insight, avoiding corporate fluff or needless censorship. "
            "When provided with tools within <tools></tools> XML tags, use <tool_call> tags to call functions when helpful."
        ),
        "tools": ["web_search", "execute_python", "fetch_web_page", "get_system_time"],
        "temperature": 0.7,
        "is_default": True
    },
    {
        "id": "grok-build",
        "name": "Grok Build (Coder Staff)",
        "avatar": "💻",
        "description": "Specialized Staff Agent for software engineering, debugging, and Python execution.",
        "system_prompt": (
            "You are Grok Build, an elite autonomous software engineering staff agent. "
            "You write clean, modular, production-ready code. You evaluate math, data structures, and algorithms "
            "by calling execute_python tool when helpful. Provide precise explanations alongside working code."
        ),
        "tools": ["execute_python", "web_search", "get_system_time"],
        "temperature": 0.2,
        "is_default": True
    },
    {
        "id": "grok-research",
        "name": "Grok Research Staff",
        "avatar": "🔍",
        "description": "Specialized Staff Agent for deep web investigation, fact-checking, and site reading.",
        "system_prompt": (
            "You are Grok Research Staff, an expert investigative research staff agent. "
            "You synthesize real-time information from multiple web searches and deep web page readings. "
            "Provide well-structured, citation-backed reports with key takeaways."
        ),
        "tools": ["web_search", "fetch_web_page", "get_system_time"],
        "temperature": 0.5,
        "is_default": True
    }
]


class AgentStore:
    def __init__(self):
        self.file_path = os.path.abspath(AGENTS_FILE)
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            self.save_agents(DEFAULT_AGENTS)

    def load_agents(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_AGENTS

    def save_agents(self, agents):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(agents, f, indent=2, ensure_ascii=False)

    def get_agent(self, agent_id: str):
        agents = self.load_agents()
        for a in agents:
            if a["id"] == agent_id:
                return a
        return agents[0]  # Fallback to Grok Original

    def create_agent(self, name: str, description: str, system_prompt: str, tools: list, avatar: str = "🤖", temperature: float = 0.7):
        agents = self.load_agents()
        new_agent = {
            "id": f"custom-{uuid.uuid4().hex[:8]}",
            "name": name,
            "avatar": avatar,
            "description": description,
            "system_prompt": system_prompt,
            "tools": tools,
            "temperature": temperature,
            "is_default": False
        }
        agents.append(new_agent)
        self.save_agents(agents)
        return new_agent

    def delete_agent(self, agent_id: str):
        agents = self.load_agents()
        filtered = [a for a in agents if a["id"] != agent_id or a.get("is_default", False)]
        self.save_agents(filtered)
        return True
