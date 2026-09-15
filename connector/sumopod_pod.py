import os
import requests
import json

class SumoPodConnector:
    def __init__(self, pod_url=None, username=None, password=None, api_key=None):
        self.pod_url = (pod_url or os.getenv("SUMOPOD_POD_URL", "https://hermes-gwrdes.jkt8.sumopod.my.id")).rstrip('/')
        self.username = username or os.getenv("HERMES_DASHBOARD_USERNAME", "JbjUU8")
        self.password = password or os.getenv("HERMES_DASHBOARD_PASSWORD", "UxYuYKf1BJdpAAs1")
        self.api_key = api_key or os.getenv("SUMOPOD_POD_API_KEY", "sk-t9RjJEqXws30PRqj6dNprTDI")
        self.session = requests.Session()
        self._authenticated = False

    def _ensure_auth(self):
        if self._authenticated:
            return True
        try:
            resp = self.session.post(
                f"{self.pod_url}/auth/password-login",
                json={"provider": "basic", "username": self.username, "password": self.password},
                timeout=10
            )
            if resp.status_code == 200:
                self._authenticated = True
                return True
        except Exception:
            pass
        return False

class SumoPodConnector:
    def __init__(self, pod_url=None, username=None, password=None, api_key=None):
        self.pod_url = (pod_url or os.getenv("SUMOPOD_POD_URL", "https://hermes-gwrdes.jkt8.sumopod.my.id")).rstrip('/')
        self.username = username or os.getenv("HERMES_DASHBOARD_USERNAME", "JbjUU8")
        self.password = password or os.getenv("HERMES_DASHBOARD_PASSWORD", "UxYuYKf1BJdpAAs1")
        self.api_key = api_key or os.getenv("SUMOPOD_POD_API_KEY", "sk-t9RjJEqXws30PRqj6dNprTDI")
        self.session = requests.Session()
        self._authenticated = False

    def _ensure_auth(self):
        if self._authenticated:
            return True
        try:
            resp = self.session.post(
                f"{self.pod_url}/auth/password-login",
                json={"provider": "basic", "username": self.username, "password": self.password},
                timeout=10
            )
            if resp.status_code == 200:
                self._authenticated = True
                return True
        except Exception:
            pass
        return False

    def get_pod_status_info(self) -> dict:
        """Returns structured health, configuration, and model information from Hermes Pod."""
        self._ensure_auth()
        info = {
            "online": False,
            "pod_url": self.pod_url,
            "model": "Unknown",
            "webhooks_enabled": False,
            "skills_count": 0,
            "sessions_count": 0
        }
        try:
            r_config = self.session.get(f"{self.pod_url}/api/config", timeout=10)
            if r_config.status_code == 200:
                info["online"] = True
                cfg = r_config.json()
                info["model"] = cfg.get("model") or cfg.get("active_model", "nemotron-3.5-lightning-free")

            r_webhooks = self.session.get(f"{self.pod_url}/api/webhooks", timeout=10)
            if r_webhooks.status_code == 200:
                wh = r_webhooks.json()
                info["webhooks_enabled"] = wh.get("enabled", True)

            r_skills = self.session.get(f"{self.pod_url}/api/skills", timeout=10)
            if r_skills.status_code == 200:
                skills = r_skills.json()
                if isinstance(skills, list):
                    info["skills_count"] = len(skills)

            r_sessions = self.session.get(f"{self.pod_url}/api/sessions", timeout=10)
            if r_sessions.status_code == 200:
                sess_data = r_sessions.json()
                info["sessions_count"] = sess_data.get("total", len(sess_data.get("sessions", [])))
        except Exception:
            pass
        return info

    def get_pod_status(self) -> str:
        """Checks connectivity, health, and configuration of the remote Hermes Pod (Markdown)."""
        info = self.get_pod_status_info()
        if not info["online"]:
            return f"❌ Error connecting to Hermes Pod ({self.pod_url})"
        
        return (
            f"✅ **Hermes Pod Status: ONLINE & CONNECTED**\n"
            f"- **Pod URL:** {info['pod_url']}\n"
            f"- **Gateway Mode:** Multi-Agent Autonomous Pod\n"
            f"- **Active Model in Pod:** `{info['model']}`\n"
            f"- **Webhooks Gateway:** {'🟢 Enabled' if info['webhooks_enabled'] else '🔴 Disabled'}\n"
            f"- **Installed Skills:** {info['skills_count']} active skills\n"
            f"- **Recorded Sessions:** {info['sessions_count']} sessions"
        )

    def get_remote_skills_list(self) -> list:
        """Returns list of skill dictionaries from remote Hermes Pod."""
        self._ensure_auth()
        try:
            resp = self.session.get(f"{self.pod_url}/api/skills", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data if isinstance(data, list) else []
        except Exception:
            pass
        return []

    def list_remote_skills(self) -> str:
        """Fetches active modular skills installed inside the remote Hermes Pod (Markdown)."""
        skills = self.get_remote_skills_list()
        if not skills:
            return "Tidak dapat mengambil skills dari Remote Hermes Pod."
        
        summary = [f"📦 **{len(skills)} Skills Aktif di Remote Hermes Pod:**"]
        for s in skills[:20]:
            name = s.get("name") or s.get("id") or str(s)
            desc = s.get("description", "")
            summary.append(f"- **{name}**: {desc[:80]}..." if desc else f"- **{name}**")
        if len(skills) > 20:
            summary.append(f"...dan {len(skills) - 20} skills lainnya.")
        return "\n".join(summary)

    def get_remote_sessions_list(self) -> list:
        """Gets active sessions list from the remote Hermes Pod."""
        self._ensure_auth()
        try:
            resp = self.session.get(f"{self.pod_url}/api/sessions", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("sessions", [])
        except Exception:
            pass
        return []

    def get_remote_session_messages(self, session_id: str) -> list:
        """Gets message transcript for a specific session ID from remote Hermes Pod."""
        self._ensure_auth()
        try:
            resp = self.session.get(f"{self.pod_url}/api/sessions/{session_id}/messages", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("messages", [])
        except Exception:
            pass
        return []

    def trigger_webhook(self, event_name: str, payload_json: str = "{}") -> str:
        """Triggers an event to the remote Hermes Pod."""
        self._ensure_auth()
        try:
            data = json.loads(payload_json) if isinstance(payload_json, str) else payload_json
            headers = {"Authorization": f"Bearer {self.api_key}"}
            resp = self.session.post(
                f"{self.pod_url}/api/webhooks/trigger",
                json={"event": event_name, "data": data},
                headers=headers,
                timeout=15
            )
            return f"Event '{event_name}' processed by Hermes Pod (HTTP {resp.status_code})"
        except Exception as e:
            return f"Error triggering event on Hermes Pod: {str(e)}"

