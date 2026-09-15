import re
import json
from t3_app import tools

class ConnectorRouter:
    def __init__(self, enabled_tools=None, agent_store=None):
        self.enabled_tools = enabled_tools or ["delegate_to_staff", "web_search", "execute_python", "fetch_web_page", "get_system_time"]
        self.agent_store = agent_store
        
    def parse_tool_calls(self, text: str):
        """
        Parses Hermes XML <tool_call> and DSML <｜DSML｜ invoke> tags from text.
        """
        tool_calls = []
        
        # 1. Hermes <tool_call>{...}</tool_call>
        pattern_hermes = r'<tool_call>\s*({.*?})\s*</tool_call>'
        for m in re.findall(pattern_hermes, text, re.DOTALL):
            try:
                data = json.loads(m.strip())
                if "name" in data:
                    tool_calls.append(data)
            except Exception:
                try:
                    repaired = m.replace("'", '"')
                    data = json.loads(repaired.strip())
                    if "name" in data:
                        tool_calls.append(data)
                except Exception:
                    pass

        # 2. DSML / XML invoke format: <...invoke name="tool_name">...</...invoke>
        pattern_invoke = r'<[^>]*invoke\s+name=["\'](.*?)["\'][^>]*>(.*?)</[^>]*invoke>'
        for name, body in re.findall(pattern_invoke, text, re.DOTALL):
            args = {}
            # Parse parameters inside invoke tag
            param_matches = re.findall(r'<[^>]*parameter\s+name=["\'](.*?)["\'][^>]*>(.*?)</[^>]*parameter>', body, re.DOTALL)
            if param_matches:
                for p_name, p_val in param_matches:
                    try:
                        args[p_name] = json.loads(p_val.strip())
                    except Exception:
                        args[p_name] = p_val.strip()
            elif body.strip():
                try:
                    args = json.loads(body.strip())
                except Exception:
                    pass
            tool_calls.append({"name": name.strip(), "arguments": args})
            
        return tool_calls

    def execute_tool_call(self, tool_call: dict) -> dict:
        name = tool_call.get("name")
        args = tool_call.get("arguments", {})
        
        if name not in self.enabled_tools:
            result_str = f"Error: Tool '{name}' is disabled or unavailable for this agent."
        elif name == "delegate_to_staff":
            staff_id = args.get("staff_agent_id", "")
            instruction = args.get("subtask_instruction", "")
        elif name == "sumopod_get_pod_status":
            result_str = tools.sumopod_get_pod_status()
        elif name == "sumopod_list_remote_skills":
            result_str = tools.sumopod_list_remote_skills()
        elif name == "sumopod_trigger_webhook":
            ev = args.get("event_name", "task")
            payload = args.get("payload_json", "{}")
            result_str = tools.sumopod_trigger_webhook(event_name=ev, payload_json=payload)
        elif name == "gdrive_list_files":
            query = args.get("query", "")
            max_results = args.get("max_results", 10)
            result_str = tools.gdrive_list_files(query=query, max_results=max_results)
        elif name == "gdrive_read_file":
            file_id = args.get("file_id", "")
            result_str = tools.gdrive_read_file(file_id=file_id)
        elif name == "gdrive_upload_file":
            name_arg = args.get("name", "Untitled.txt")
            content_arg = args.get("content", "")
            folder_id = args.get("folder_id", "")
            result_str = tools.gdrive_upload_file(name=name_arg, content=content_arg, folder_id=folder_id)
        elif name == "web_search":
            query = args.get("query", "")
            result_str = tools.web_search(query)
        elif name == "execute_python":
            code = args.get("code", "")
            result_str = tools.execute_python(code)
        elif name == "fetch_web_page":
            url = args.get("url", "")
            result_str = tools.fetch_web_page(url)
        elif name == "get_system_time":
            result_str = tools.get_system_time()
        else:
            result_str = f"Error: Unknown tool '{name}'."
            
        return {
            "name": name,
            "result": result_str,
            "xml_response": f"<tool_response>\n{{\"name\": \"{name}\", \"content\": {json.dumps(result_str)}}}\n</tool_response>"
        }

