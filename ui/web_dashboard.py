import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional

from hermes.agent_store import AgentStore
from hermes.brain import HermesBrain

app = FastAPI(title="Grok Bot Clone - Hermes AI")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

agent_store = AgentStore()
brain = HermesBrain()

class CreateAgentRequest(BaseModel):
    name: str
    description: str
    system_prompt: str
    tools: List[str] = Field(default_factory=lambda: ["web_search", "execute_python"])
    avatar: str = "🤖"
    temperature: float = 0.7

class ChatRequest(BaseModel):
    messages: List[dict]
    agent_id: Optional[str] = "grok-original"
    mode: Optional[str] = "fun"  # fun, regular, think

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/agents")
def get_agents():
    return agent_store.load_agents()

@app.post("/api/agents")
def create_agent(req: CreateAgentRequest):
    new_agent = agent_store.create_agent(
        name=req.name,
        description=req.description,
        system_prompt=req.system_prompt,
        tools=req.tools,
        avatar=req.avatar,
        temperature=req.temperature
    )
    return new_agent

@app.delete("/api/agents/{agent_id}")
def delete_agent(agent_id: str):
    success = agent_store.delete_agent(agent_id)
    return {"success": success}

from connector.sumopod_pod import SumoPodConnector

sumopod_conn = SumoPodConnector()

@app.get("/api/pod/status")
def get_pod_status():
    return sumopod_conn.get_pod_status_info()

@app.get("/api/pod/skills")
def get_pod_skills():
    return sumopod_conn.get_remote_skills_list()

@app.get("/api/pod/sessions")
def get_pod_sessions():
    return sumopod_conn.get_remote_sessions_list()

@app.get("/api/pod/sessions/{session_id}/messages")
def get_pod_session_messages(session_id: str):
    return sumopod_conn.get_remote_session_messages(session_id)

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    agent_config = agent_store.get_agent(req.agent_id)
    
    def event_stream():
        for event in brain.generate_chat_response(req.messages, agent_config, req.mode):
            yield f"data: {json.dumps(event)}\n\n"
            
    return StreamingResponse(event_stream(), media_type="text/event-stream")

