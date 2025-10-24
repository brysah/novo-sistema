import json
NEWSLETTER_URLS_FILE = "newsletter_urls.json"
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from models import ProgressTask, TaskStatus
from progress_manager import progress_manager
import subprocess
import threading
import sys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Específico para Next.js
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

class StartRequest(BaseModel):
    emails: List[str]
    urls: List[str]
    speed: str = "slow"

@app.get("/newsletter/urls")
def get_newsletter_urls():
    try:
        with open(NEWSLETTER_URLS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"urls": data.get("urls", [])}
    except FileNotFoundError:
        return {"urls": []}

@app.post("/newsletter/urls")
def save_newsletter_urls(payload: dict):
    urls = payload.get("urls", [])
    with open(NEWSLETTER_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump({"urls": urls}, f, indent=2, ensure_ascii=False)
    return {"status": "saved", "count": len(urls)}    

def load_newsletter_urls():
        import json
        """Carrega a lista de URLs das newsletters do arquivo JSON."""
        if not "newsletters.json".exists():
            return []
        try:
            with open("newsletters.json", 'r', encoding='utf-8') as f:
                urls = json.load(f)
                return [url for url in urls if isinstance(url, str) and url.strip()]
        except json.JSONDecodeError:
            return []

@app.post("/start")
def start_automation(req: StartRequest):
    # Resetar progresso
    progress_manager.reset()
    # Montar lista de tarefas
    tasks = [
        {"email": email, "url": url, "status": TaskStatus.pending, "message": None}
        for email in req.emails for url in req.urls
    ]
    progress_manager.start(tasks)
    import json
    input_data = {
        "emails": req.emails,
        "urls": req.urls,
        "speed": req.speed
    }
    with open("input_data.json", "w", encoding="utf-8") as f:
        json.dump(input_data, f)
    def run_automator():
        import runpy
        import sys
        sys.argv = ["newsletter_automator_professional.py", "input_data.json"]
        runpy.run_path("newsletter_automator_professional.py", run_name="__main__")
    threading.Thread(target=run_automator, daemon=True).start()
    return {"status": "started", "total": len(tasks)}



@app.post("/stop")
def stop_automation():
    # Não implementado: depende de controle do automator
    progress_manager.reset()
    return {"status": "stopped"}

@app.post("/clear")
def clear_progress():
    progress_manager.reset()
    return {"status": "cleared"}

@app.get("/tasks", response_model=List[ProgressTask])
def get_tasks():
    return progress_manager.get_tasks()

@app.get("/status")
def get_status():
    return progress_manager.get_status()

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, status: TaskStatus, message: str = None):
    progress_manager.update_task(task_id, status, message)
    return {"status": "updated"}




if __name__ == "__main__":
    # Start the app with uvicorn when executing `py main.py` directly.
    # Use 127.0.0.1 for local development; change host to '0.0.0.0' if you
    # want external access on your network.
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
