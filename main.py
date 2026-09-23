from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from remote_whatsapp import router as whatsapp_router

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

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Kavya CRM AI Service is running!"}
