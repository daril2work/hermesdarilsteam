---
title: Grok Bot Clone
emoji: ⚡
colorFrom: gray
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# 🤖 Grok Bot Clone (Hermes 3 AI + SumoPod Gateway)

Autonomous multi-agent assistant inspired by Grok, powered by Nous Hermes 3 AI and SumoPod Gateway.

## ✨ Features
- **Grok Modes:** Fun (witty & sarcastic), Regular (fast & objective), and Think (extended reasoning chain-of-thought).
- **Multi-Agent Hierarchy:** Chief of Staff manager with delegation to Grok Build (Python coder), Grok Research, and custom staff agents.
- **Real-Time Agentic Tools:** Live web search via DuckDuckGo, Python code execution sandbox, deep web page reader, and system clock.
- **FastAPI + SSE Streaming:** Live streaming responses and tool execution activity cards.

## 🚀 Environment Variables (Hugging Face Secrets)
In your Hugging Face Space settings (**Settings > Variables and secrets**), add the following secrets:
- `SUMOPOD_API_BASE`: `https://ai.sumopod.com/v1`
- `SUMOPOD_API_KEY`: Your SumoPod AI Gateway API Key
- `SUMOPOD_MODEL_NAME`: `deepseek-v4-flash` or `nous-hermes-3`
