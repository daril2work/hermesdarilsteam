import uvicorn
from config import HOST, PORT
from ui.web_dashboard import app

if __name__ == "__main__":
    print(f"\n=======================================================")
    print(f"   Grok-Like Bot Server (Hermes 3 AI + SumoPod Gateway)")
    print(f"=======================================================")
    print(f"   Running Web UI Dashboard at: http://localhost:{PORT}")
    print(f"=======================================================\n")
    
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
