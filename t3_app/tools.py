import sys
import io
import datetime
import requests
import json

def get_system_time() -> str:
    """Returns current system timestamp."""
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S (%A)')}"

def web_search(query: str, max_results: int = 5) -> str:
    """Performs web search to retrieve real-time data."""
    results = []
    # Lazy import duckduckgo_search to avoid boot delay
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(query, max_results=max_results))
            for item in ddg_results:
                results.append(f"- **{item.get('title')}**: {item.get('body')} (URL: {item.get('href')})")
    except Exception as e:
        results.append(f"Search notice: {str(e)}")
    
    if not results:
        try:
            resp = requests.get(f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}", headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }, timeout=5)
            if resp.status_code == 200:
                results.append("Search executed via DuckDuckGo HTML fallback.")
        except Exception as ex:
            results.append(f"Search fallback notice: {str(ex)}")
            
    return "\n".join(results) if results else "No search results found."

def execute_python(code: str) -> str:
    """Executes Python code dynamically in a captured environment (Grok Build Engine)."""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    captured_stdout = io.StringIO()
    captured_stderr = io.StringIO()
    
    sys.stdout = captured_stdout
    sys.stderr = captured_stderr
    
    global_scope = {"sys": sys, "datetime": datetime, "requests": requests, "json": json}
    local_scope = {}
    
    error_str = None
    try:
        exec(code, global_scope, local_scope)
    except Exception as e:
        error_str = f"Execution Exception: {type(e).__name__}: {str(e)}"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
    out = captured_stdout.getvalue()
    err = captured_stderr.getvalue()
    
    output_parts = []
    if out.strip():
        output_parts.append(f"STDOUT:\n{out.strip()}")
    if err.strip():
        output_parts.append(f"STDERR:\n{err.strip()}")
    if error_str:
        output_parts.append(error_str)
    if not output_parts and local_scope:
        output_parts.append(f"VARIABLES: {local_scope}")
    if not output_parts:
        output_parts.append("Code executed successfully (no output printed).")
        
    return "\n---\n".join(output_parts)

def fetch_web_page(url: str) -> str:
    """Fetches text content of a web page for deep research."""
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=8)
        if resp.status_code == 200:
            text = resp.text
            import re
            text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
            text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<.*?>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:3000] + ("\n...[Content Truncated]" if len(text) > 3000 else "")
        else:
            return f"Failed to fetch web page. HTTP Status Code: {resp.status_code}"
    except Exception as e:
        return f"Error fetching web page: {str(e)}"

# Tools Schema Definitions for Hermes XML Tool Calling
AVAILABLE_TOOLS = [
    {
        "name": "delegate_to_staff",
        "description": "Chief of Staff tool: Delegate a specific sub-task to a specialized Staff Agent (e.g. 'grok-build', 'grok-research', or custom staff agent).",
        "parameters": {
            "type": "object",
            "properties": {
                "staff_agent_id": {"type": "string", "description": "The ID of the staff agent (e.g. 'grok-build', 'grok-research')."},
                "subtask_instruction": {"type": "string", "description": "Clear instruction for the staff agent to execute."}
            },
            "required": ["staff_agent_id", "subtask_instruction"]
        }
    },
    {
        "name": "web_search",
        "description": "Perform a web search to fetch real-time info, news, or factual data.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query string."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "execute_python",
        "description": "Execute Python code to evaluate mathematical expressions, algorithms, or process data.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Valid Python code to execute."}
            },
            "required": ["code"]
        }
    },
    {
        "name": "fetch_web_page",
        "description": "Fetch and extract text content from a web page URL for deep research.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The full HTTP/HTTPS URL."}
            },
            "required": ["url"]
        }
    },
    {
        "name": "get_system_time",
        "description": "Get current real-time system date and timestamp.",
        "parameters": {"type": "object", "properties": {}},
        "required": []
    }
]
