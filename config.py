import os
from dotenv import load_dotenv

# Load environment variables
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_BASE_DIR, ".env"), override=True)
load_dotenv(override=True)

SUMOPOD_API_BASE = os.getenv("SUMOPOD_API_BASE", "https://ai.sumopod.com/v1")
SUMOPOD_API_KEY = os.getenv("SUMOPOD_API_KEY", "")
SUMOPOD_MODEL_NAME = os.getenv("SUMOPOD_MODEL_NAME", "nous-hermes-3")
HERMES_POD_URL = os.getenv("HERMES_POD_URL", "https://hermes-gwrdes.jkt8.sumopod.my.id")
HERMES_POD_USERNAME = os.getenv("HERMES_POD_USERNAME", "JbjUU8")
HERMES_POD_PASSWORD = os.getenv("HERMES_POD_PASSWORD", "UxYuYKf1BJdpAAs1")
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

# Persona System Prompts for Grok Modes
GROK_PERSONAS = {
    "fun": (
        "You are Grok, an AI modeled after the Hitchhiker's Guide to the Galaxy. "
        "You are witty, highly intelligent, direct, rebellious, and humorous with a touch of sarcasm. "
        "You answer questions with candor and sharp insight, avoiding corporate fluff or needless censorship. "
        "When provided with tools within <tools></tools> XML tags, use <tool_call> tags to call functions when helpful."
    ),
    "regular": (
        "You are Grok, a smart, direct, and highly efficient AI assistant. "
        "Provide objective, clear, concise, and accurate answers to user queries without fluff. "
        "When provided with tools within <tools></tools> XML tags, use <tool_call> tags to call functions when helpful."
    ),
    "think": (
        "You are Grok in Extended Reasoning Mode. "
        "First, analyze the query step-by-step using deep logical chain-of-thought thinking inside a <think>...</think> block. "
        "After thoroughly analyzing the problem, provide the final comprehensive, precise solution. "
        "When tools are available, call them using <tool_call> tags when necessary."
    )
}
