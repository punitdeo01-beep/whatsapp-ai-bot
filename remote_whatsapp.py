from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

def generate_chat_reply(text: str) -> str:
    api_key = "AIzaSyBOO5uDLHJpK5FTBV6wTppqIhMTYsqZlhU"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": f"You are Kavya, a smart and helpful customer support agent for Kavya Traders. Reply concisely in Hinglish. User says: {text}"}]}]
    }
    try:
        resp = requests.post(url, json=payload, timeout=20).json()
        return resp["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print("Gemini Error:", e)
        return "Sorry, abhi main thoda busy hu (AI Error)."

load_dotenv()
router = APIRouter()

META_PHONE_ID = "1006511319205859"
META_TOKEN = "EAAM8ANF1NH4BSnrNbpn77IE1IheKbZCI6fAKDkr0vy4fydKSSrNnOXh6TMbx9tECGaDoOLjDXP34xG4jZAVL9MQAZCgZBw0WihRzYakkU1ym7OzZBTV7SYoplgcRDZBPcrd0AS3tf0hcGbMJp3BBkJmg0J7fp2FNGBy2ZCPPmg2b29iG0aJrazPdL5lnjTZCy5NZAAYXDZC01tmAjtmiZCUQl9RLgG936XIxWGNajGYKQZDZD"
VERIFY_TOKEN = "KAVYA_CRM_VERIFY"

@router.get("/whatsapp/webhook")
async def verify_meta_webhook(request: Request):
    """
    Webhook verification endpoint for Meta API
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=403)

@router.post("/whatsapp/webhook")
async def meta_webhook(request: Request):
    """
    Webhook endpoint to receive incoming messages from Meta WhatsApp API.
    """
    try:
        payload = await request.json()
        print("Incoming Meta WhatsApp Payload:", payload)
        
        text = ""
        sender_phone = ""
        
        # Parse Meta Webhook
        try:
            if "entry" in payload:
                changes = payload["entry"][0]["changes"][0]["value"]
                if "messages" in changes:
                    msg = changes["messages"][0]
                    sender_phone = msg.get("from", "")
                    if "text" in msg:
                        text = msg["text"].get("body", "")
        except Exception:
            pass
            
        if not text or not sender_phone:
            return {"status": "ignored", "reason": "No text or sender found"}

        print(f"Received from {sender_phone}: {text}")
        
        # Generate AI Reply
        reply_text = generate_chat_reply(text)
        print(f"AI Reply: {reply_text}")
        
        # Send Reply via Meta Graph API
        url = f"https://graph.facebook.com/v17.0/{META_PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {META_TOKEN}",
            "Content-Type": "application/json"
        }
        out_payload = {
            "messaging_product": "whatsapp",
            "to": sender_phone,
            "type": "text",
            "text": {"body": reply_text}
        }
        resp = requests.post(url, headers=headers, json=out_payload, timeout=10)
        print("Meta API Response:", resp.text)
        
        return {"status": "success", "message": "Reply sent"}
        
    except Exception as e:
        print("Webhook Error:", str(e))
        return {"status": "error", "message": str(e)}
