import json
import requests
from config import SUMOPOD_API_BASE, SUMOPOD_API_KEY, SUMOPOD_MODEL_NAME, GROK_PERSONAS
from t3_app.tools import AVAILABLE_TOOLS
from connector.router import ConnectorRouter

class HermesBrain:
    def __init__(self, api_base=None, api_key=None, model_name=None):
        self.api_base = (api_base or SUMOPOD_API_BASE).rstrip('/')
        self.api_key = api_key or SUMOPOD_API_KEY
        self.model_name = model_name or SUMOPOD_MODEL_NAME

    def _build_system_prompt(self, agent_config: dict, mode: str = "fun") -> str:
        base_prompt = agent_config.get("system_prompt") or GROK_PERSONAS.get(mode, GROK_PERSONAS["fun"])
        
        # Inject Grok mode overrides if present
        if mode == "think" and "<think>" not in base_prompt:
            base_prompt += "\n" + GROK_PERSONAS["think"]
        elif mode == "regular" and agent_config.get("is_default"):
            base_prompt = GROK_PERSONAS["regular"]
            
        # Format XML Tools
        agent_tools = agent_config.get("tools", [])
        active_tools = [t for t in AVAILABLE_TOOLS if t["name"] in agent_tools]
        
        if active_tools:
            tools_xml = "<tools>\n"
            for t in active_tools:
                tools_xml += json.dumps(t) + "\n"
            tools_xml += "</tools>\n"
            tools_xml += (
                "For each function call return a json object with function name and arguments "
                "within <tool_call></tool_call> XML tags as follows:\n"
                "<tool_call>\n"
                "{\"name\": \"<function-name>\", \"arguments\": <args-dict>}\n"
                "</tool_call>"
            )
            base_prompt += f"\n\nYou are provided with function signatures within <tools></tools> XML tags. You may call tools when needed.\n{tools_xml}"
            
        return base_prompt

    def generate_chat_response(self, messages: list, agent_config: dict, mode: str = "fun"):
        """
        Executes multi-step ReAct Agent loop via SumoPod AI Gateway.
        Yields status updates and final streaming text.
        """
        system_prompt = self._build_system_prompt(agent_config, mode)
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        router = ConnectorRouter(enabled_tools=agent_config.get("tools", []))
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        
        max_react_turns = 3
        current_turn = 0
        
        while current_turn < max_react_turns:
            current_turn += 1
            payload = {
                "model": self.model_name,
                "messages": full_messages,
                "temperature": agent_config.get("temperature", 0.7),
                "stream": False
            }
            
            try:
                resp = requests.post(f"{self.api_base}/chat/completions", json=payload, headers=headers, timeout=60)
                if resp.status_code != 200:
                    yield {
                        "type": "error",
                        "content": f"SumoPod Gateway Error ({resp.status_code}): {resp.text}"
                    }
                    return
                
                res_data = resp.json()
                assistant_content = res_data["choices"][0]["message"]["content"]
            except Exception as e:
                # Fallback mock response for testing if gateway URL is offline/unreachable
                yield {
                    "type": "warning",
                    "content": f"Notice: Could not connect to SumoPod Gateway ({str(e)}). Generating fallback response."
                }
                assistant_content = f"Greetings! I am {agent_config.get('name', 'Grok')}. How can I assist you today?"
            
            # Check for XML tool calls
            tool_calls = router.parse_tool_calls(assistant_content)
            
            if not tool_calls:
                # No more tools called; deliver final answer
                yield {"type": "content", "content": assistant_content}
                return
            
            # Tools called! Execute each tool and emit activity cards
            for call in tool_calls:
                call_name = call.get("name")
                call_args = call.get("arguments", {})
                
                if call_name == "delegate_to_staff":
                    yield {
                        "type": "delegation_call",
                        "staff_agent_id": call_args.get("staff_agent_id"),
                        "instruction": call_args.get("subtask_instruction")
                    }
                else:
                    yield {
                        "type": "tool_call",
                        "tool_name": call_name,
                        "arguments": call_args
                    }
                
                exec_result = router.execute_tool_call(call)
                
                yield {
                    "type": "tool_result",
                    "tool_name": call_name,
                    "result": exec_result["result"]
                }
                
                # Append tool call and tool response to message history for next turn
                full_messages.append({"role": "assistant", "content": f"<tool_call>\n{json.dumps(call)}\n</tool_call>"})
                full_messages.append({"role": "user", "content": exec_result["xml_response"]})
                
        yield {"type": "content", "content": assistant_content}

