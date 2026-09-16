import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

from ui.web_dashboard import app

# Check for Gradio support (native on Hugging Face Gradio Spaces)
try:
    import gradio as gr
    demo = gr.Blocks(title="Grok Bot Engine")
    with demo:
        gr.Markdown("# 🤖 Grok Bot (Hermes 3 AI) Backend Active\nVisit the root `/` to access the full Grok Dark Mode UI.")
    # Mount Gradio on /gradio so Hugging Face validates the Gradio Space, while root "/" serves our Grok UI
    application = gr.mount_gradio_app(app, demo, path="/gradio")
except ImportError:
    application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("app:application", host="0.0.0.0", port=port, reload=False)
