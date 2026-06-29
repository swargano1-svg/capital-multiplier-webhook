from fastapi import FastAPI, Request
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

app = FastAPI(title="Capital Multiplier Webhook")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Symbol wise Entry Storage
entries = {}


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

    data = await request.json()

    print(data)

    symbol = data.get("symbol", "")
    symbol = symbol.replace("NSE:", "").replace("-EQ", "")

    side = data.get("side")
    status = data.get("status")
    message = data.get("message", "")
    reason = data.get("omsMessage", "")
    price = float(data.get("tradedPrice", 0))

    ist = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%d-%m-%Y %I:%M:%S %p")

    # -------------------------
    # BUY EXECUTED
    # -------------------------
    if status == 2 and side == 1:

        entries[symbol] = price

        send_telegram(
f"""🟢 BUY EXECUTED

📈 Symbol : {symbol}

💰 Entry : ₹{price:.2f}

🕒 {ist}

━━━━━━━━━━━━━━
Capital Multiplier"""
        )

    # -------------------------
    # SELL EXECUTED
    # -------------------------
    elif status == 2 and side == -1:

        entry = entries.get(symbol)

        if entry:

            profit = ((price - entry) / entry) * 100

            emoji = "🟢" if profit >= 0 else "🔴"

            send_telegram(
f"""🔴 SELL EXECUTED

📈 Symbol : {symbol}

💰 Entry : ₹{entry:.2f}
💰 Exit  : ₹{price:.2f}

{emoji} Profit : {profit:.2f}%

🕒 {ist}

━━━━━━━━━━━━━━
Capital Multiplier"""
            )

            entries.pop(symbol, None)

        else:

            send_telegram(
f"""🔴 SELL EXECUTED

📈 Symbol : {symbol}

💰 Exit : ₹{price:.2f}

⚠ Entry Price Not Found

🕒 {ist}

━━━━━━━━━━━━━━
Capital Multiplier"""
            )

    # -------------------------
    # REJECTED
    # -------------------------
    elif message.lower() == "rejected":

        send_telegram(
f"""❌ ORDER REJECTED

📈 Symbol : {symbol}

Reason

{reason}

🕒 {ist}

━━━━━━━━━━━━━━
Capital Multiplier"""
        )

    # -------------------------
    # CANCELLED
    # -------------------------
    elif message.lower() == "cancelled":

        send_telegram(
f"""⚠ ORDER CANCELLED

📈 Symbol : {symbol}

🕒 {ist}

━━━━━━━━━━━━━━
Capital Multiplier"""
        )

    return {"success": True}
