from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import threading
from remote_whatsapp import router as whatsapp_router
from calling_agent import LiveVoiceAgent

app = FastAPI(title="Kavya CRM AI Service")

# Allow CORS for Next.js CRM frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WhatsApp Router
app.include_router(whatsapp_router)

# Global Voice Agent Instance
agent = None
agent_thread = None

def start_agent_thread():
    global agent
    try:
        asyncio.run(agent.run())
    except Exception as e:
        print(f"Agent stopped or crashed: {e}")

@app.post("/voice/start")
async def start_voice_agent(background_tasks: BackgroundTasks):
    global agent, agent_thread
    if agent is not None and agent.is_running:
        return {"status": "error", "message": "Voice agent is already running"}
    
    agent = LiveVoiceAgent()
    agent_thread = threading.Thread(target=start_agent_thread, daemon=True)
    agent_thread.start()
    
    return {"status": "success", "message": "Voice assistant started successfully"}

@app.post("/voice/stop")
async def stop_voice_agent():
    global agent
    if agent is None or not agent.is_running:
        return {"status": "error", "message": "Voice agent is not running"}
    
    agent.stop()
    agent = None
    return {"status": "success", "message": "Voice assistant stopped successfully"}

@app.get("/voice/status")
async def get_voice_status():
    global agent
    is_running = agent is not None and agent.is_running
    return {"status": "success", "is_running": is_running}

@app.post("/api/vobiz/answer/{task_id}")
@app.get("/api/vobiz/answer/{task_id}")
async def vobiz_answer(task_id: str):
    # This is what Vobiz will execute when the call is answered
    return {
        "action": "talk",
        "text": "Hello, this is a test call from Kavya CRM AI. Have a great day!"
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
