from fastapi import FastAPI, Request, HTTPException
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

app = FastAPI(title="Capital Multiplier Webhook")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


@app.get("/")
def home():
    return {
        "status": "running",
        "project": "Capital Multiplier",
        "broker": "FYERS"
    }


def send_telegram(message: str):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=10
    )


@app.post("/webhook")
async def webhook(request: Request):

    secret = request.headers.get("X-Webhook-Secret")

    if WEBHOOK_SECRET:

        if secret != WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid Secret")

    data = await request.json()

    print(data)

    ist = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d-%m-%Y %I:%M:%S %p")

    message = f"""
📢 FYERS Alert

Time : {ist}

Payload

{data}
"""

    send_telegram(message)

    return {
        "success": True
    }
