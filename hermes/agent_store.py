import json
import uuid
import db

class AgentStore:
    def __init__(self):
        db.init_db()

    def load_agents(self):
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents ORDER BY is_default DESC, created_at ASC")
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for r in rows:
            agent_dict = dict(r)
            try:
                agent_dict["tools"] = json.loads(agent_dict["tools"])
            except Exception:
                agent_dict["tools"] = ["web_search", "execute_python"]
            agent_dict["is_default"] = bool(agent_dict["is_default"])
            result.append(agent_dict)
        return result

    def get_agent(self, agent_id: str):
        agents = self.load_agents()
        for a in agents:
            if a["id"] == agent_id:
                return a
        return agents[0]  # Fallback to Chief of Staff / Grok Original

    def create_agent(self, name: str, description: str, system_prompt: str, tools: list, avatar: str = "🤖", temperature: float = 0.7):
        conn = db.get_db()
        cursor = conn.cursor()
        
        agent_id = f"custom-{uuid.uuid4().hex[:8]}"
        tools_json = json.dumps(tools)
        
        cursor.execute("""
        INSERT INTO agents (id, name, avatar, description, system_prompt, tools, temperature, is_default)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (agent_id, name, avatar, description, system_prompt, tools_json, temperature))
        
        conn.commit()
        conn.close()
        
        return self.get_agent(agent_id)

    def delete_agent(self, agent_id: str):
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agents WHERE id = ? AND is_default = 0", (agent_id,))
        conn.commit()
        conn.close()
        return True
