import sqlite3
import json
import os
import uuid
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grok_bot.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Agents Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        avatar TEXT NOT NULL,
        description TEXT,
        system_prompt TEXT NOT NULL,
        tools TEXT NOT NULL,
        temperature REAL DEFAULT 0.7,
        is_default INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Conversations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 3. Messages Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    
    # Seed default agents if empty
    cursor.execute("SELECT COUNT(*) FROM agents")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_default_agents(conn)
        
    conn.close()

def seed_default_agents(conn):
    cursor = conn.cursor()
    defaults = [
        (
            "chief-of-staff",
            "Chief of Staff 👑",
            "👑",
            "Leader Manager Agent that orchestrates and delegates sub-tasks to specialized Staff Agents.",
            (
                "You are the Chief of Staff Agent, the executive leader and manager of the Grok AI Multi-Agent System. "
                "Your role is to orchestrate complex user requests by breaking them down into clear sub-tasks, "
                "delegating tasks to specialized Staff Agents using the <tool_call>{\"name\": \"delegate_to_staff\", \"arguments\": {\"staff_agent_id\": \"...\", \"subtask_instruction\": \"...\"}}</tool_call> tool, "
                "evaluating their staff responses, and synthesizing a comprehensive executive summary for the user."
            ),
            json.dumps(["delegate_to_staff", "web_search", "execute_python", "fetch_web_page", "get_system_time"]),
            0.5,
            1
        ),
        (
            "grok-original",
            "Grok Original",
            "🤖",
            "Iconic witty, direct, highly intelligent, and unfiltered Grok AI.",
            (
                "You are Grok, an AI modeled after the Hitchhiker's Guide to the Galaxy. "
                "You are witty, highly intelligent, direct, rebellious, and humorous with a touch of sarcasm. "
                "You answer questions with candor and sharp insight, avoiding corporate fluff or needless censorship. "
                "When provided with tools within <tools></tools> XML tags, use <tool_call> tags to call functions when helpful."
            ),
            json.dumps(["web_search", "execute_python", "fetch_web_page", "get_system_time"]),
            0.7,
            1
        ),
        (
            "grok-build",
            "Grok Build (Coder Staff)",
            "💻",
            "Specialized Staff Agent for software engineering, debugging, and Python execution.",
            (
                "You are Grok Build, an elite autonomous software engineering staff agent. "
                "You write clean, modular, production-ready code. You evaluate math, data structures, and algorithms "
                "by calling execute_python tool when helpful. Provide precise explanations alongside working code."
            ),
            json.dumps(["execute_python", "web_search", "get_system_time"]),
            0.2,
            1
        ),
        (
            "grok-research",
            "Grok Research Staff",
            "🔍",
            "Specialized Staff Agent for deep web investigation, fact-checking, and site reading.",
            (
                "You are Grok Research Staff, an expert investigative research staff agent. "
                "You synthesize real-time information from multiple web searches and deep web page readings. "
                "Provide well-structured, citation-backed reports with key takeaways."
            ),
            json.dumps(["web_search", "fetch_web_page", "get_system_time"]),
            0.5,
            1
        )
    ]
    
    for agent in defaults:
        cursor.execute("""
        INSERT INTO agents (id, name, avatar, description, system_prompt, tools, temperature, is_default)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, agent)
    
    conn.commit()

# Run database initialization on module load
init_db()
