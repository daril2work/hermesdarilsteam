import sys
import io
import datetime
import requests
import json

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

def get_system_time() -> str:
    """Returns current system timestamp."""
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S (%A)')}"

def web_search(query: str, max_results: int = 5) -> str:
    """Performs web search to retrieve real-time data."""
    results = []
    if DDGS is not None:
        try:
            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(query, max_results=max_results))
                for item in ddg_results:
                    results.append(f"- **{item.get('title')}**: {item.get('body')} (URL: {item.get('href')})")
        except Exception as e:
            results.append(f"DuckDuckGo search error: {str(e)}")
    
    if not results:
        # Fallback HTTP search query snippet
        try:
            resp = requests.get(f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}", headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }, timeout=8)
            if resp.status_code == 200:
                results.append("Search executed via DuckDuckGo HTML fallback.")
        except Exception as ex:
            results.append(f"Search fallback error: {str(ex)}")
            
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
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=10)
        if resp.status_code == 200:
            # Strip simple HTML tags
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

def gdrive_list_files(query: str = "", max_results: int = 10) -> str:
    """Lists files in Google Drive."""
    try:
        from connector.google_drive import GoogleDriveConnector
        gdc = GoogleDriveConnector()
        return gdc.list_files(query=query, max_results=max_results)
    except Exception as e:
        return f"Google Drive error: {str(e)}"

def gdrive_read_file(file_id: str) -> str:
    """Reads content of a Google Drive file or document."""
    try:
        from connector.google_drive import GoogleDriveConnector
        gdc = GoogleDriveConnector()
        return gdc.read_file(file_id=file_id)
    except Exception as e:
        return f"Google Drive read error: {str(e)}"

def gdrive_upload_file(name: str, content: str, folder_id: str = "") -> str:
    """Uploads a new text document to Google Drive."""
    try:
        from connector.google_drive import GoogleDriveConnector
        gdc = GoogleDriveConnector()
        return gdc.upload_text_file(name=name, content=content, folder_id=folder_id)
    except Exception as e:
        return f"Google Drive upload error: {str(e)}"

def sumopod_get_pod_status() -> str:
    """Checks the status and health of the remote SumoPod Hermes Pod."""
    try:
        from connector.sumopod_pod import SumoPodConnector
        spc = SumoPodConnector()
        return spc.get_pod_status()
    except Exception as e:
        return f"Error connecting to SumoPod Pod: {str(e)}"

def sumopod_list_remote_skills() -> str:
    """Lists the 53 skills installed in the remote SumoPod Hermes Pod."""
    try:
        from connector.sumopod_pod import SumoPodConnector
        spc = SumoPodConnector()
        return spc.list_remote_skills()
    except Exception as e:
        return f"Error listing skills from SumoPod Pod: {str(e)}"

def sumopod_trigger_webhook(event_name: str, payload_json: str = "{}") -> str:
    """Sends a webhook task trigger to the remote SumoPod Hermes Pod."""
    try:
        from connector.sumopod_pod import SumoPodConnector
        spc = SumoPodConnector()
        return spc.trigger_webhook(event_name=event_name, payload_json=payload_json)
    except Exception as e:
        return f"Error triggering webhook on SumoPod Pod: {str(e)}"

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
        "name": "sumopod_get_pod_status",
        "description": "Check connection status, active model, and health of the user's remote Hermes Pod on SumoPod (hermes-gwrdes.jkt8.sumopod.my.id).",
        "parameters": {"type": "object", "properties": {}},
        "required": []
    },
    {
        "name": "sumopod_list_remote_skills",
        "description": "List all 53 modular AI skills installed and running inside the user's remote Hermes Pod on SumoPod.",
        "parameters": {"type": "object", "properties": {}},
        "required": []
    },
    {
        "name": "sumopod_trigger_webhook",
        "description": "Trigger an automated task or event on the remote SumoPod Hermes Pod via Inbound Webhook.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_name": {"type": "string", "description": "The event name (e.g. 'research_task', 'daily_briefing')."},
                "payload_json": {"type": "string", "description": "JSON string data to pass with the event."}
            },
            "required": ["event_name"]
        }
    },
    {
        "name": "gdrive_list_files",
        "description": "List or search files and documents in user's Google Drive storage.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Optional search term to filter files by title or content."},
                "max_results": {"type": "integer", "description": "Maximum number of files to return (default 10)."}
            },
            "required": []
        }
    },
    {
        "name": "gdrive_read_file",
        "description": "Read and extract text content from a Google Drive file, Google Doc, or Google Sheet using file_id.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_id": {"type": "string", "description": "The Google Drive file ID."}
            },
            "required": ["file_id"]
        }
    },
    {
        "name": "gdrive_upload_file",
        "description": "Create or upload a new text file/document to Google Drive.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Filename (e.g. 'Rangkuman.txt' or 'Notes.md')."},
                "content": {"type": "string", "description": "Text content to save into the file."}
            },
            "required": ["name", "content"]
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

