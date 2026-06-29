from fastapi import FastAPI, Request
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

from storage import (
    save_trade,
    get_trade,
    delete_trade,
    is_duplicate
)

app = FastAPI(title="Capital Multiplier V3")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ==========================================
# Home
# ==========================================

@app.get("/")
def home():

    return {

        "status": "running",

        "version": "V3",

        "project": "Capital Multiplier",

        "broker": "FYERS"

    }


# ==========================================
# Telegram
# ==========================================

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


# ==========================================
# Helpers
# ==========================================

def clean_symbol(symbol):

    return symbol.replace("NSE:", "").replace("-EQ", "")


def current_time():

    return datetime.now(

        ZoneInfo("Asia/Kolkata")

    ).strftime("%d-%m-%Y %I:%M:%S %p")


def line():

    return "━━━━━━━━━━━━━━━━━━━━"


# ==========================================
# Webhook
# ==========================================

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("=" * 30)
    print("PAYLOAD")
    print(data)
    print("=" * 30)

    order_id = str(data.get("id", ""))

    if order_id:

        if is_duplicate(order_id):

            print("Duplicate Order Ignored")

            return {

                "duplicate": True

            }

    symbol = clean_symbol(

        data.get("symbol", "")

    )

    side = data.get("side")

    status = data.get("status")

    message = str(

        data.get("message", "")

    ).lower()

    reason = data.get(

        "omsMessage", ""

    )

    price = float(

        data.get("tradedPrice", 0)

    )

    ist = current_time()
    # ==========================================
    # BUY EXECUTED
    # ==========================================

    if status == 2 and side == 1:

        existing_trade = get_trade(symbol)

        if existing_trade:

            send_telegram(
f"""{line()}

⚠ BUY IGNORED

📈 Symbol : {symbol}

Reason

Already Active Position Exists

{line()}
Capital Multiplier"""
            )

            return {"success": True}

        save_trade(

            symbol,

            price,

            ist

        )

        send_telegram(
f"""{line()}

🟢 BUY EXECUTED

📈 Symbol : {symbol}

💰 Entry : ₹{price:.2f}

🕒 {ist}

{line()}
Capital Multiplier"""
        )

        return {

            "success": True

        }


    # ==========================================
    # SELL EXECUTED
    # ==========================================

    elif status == 2 and side == -1:

        trade = get_trade(symbol)

        if trade:

            entry = float(

                trade["entry"]

            )

            entry_time = trade["entry_time"]

            profit = (

                (price - entry)

                / entry

            ) * 100

            emoji = "🟢"

            if profit < 0:

                emoji = "🔴"
            send_telegram(
f"""{line()}

🔴 SELL EXECUTED

📈 Symbol : {symbol}

💰 Entry : ₹{entry:.2f}

💰 Exit : ₹{price:.2f}

{emoji} Profit : {profit:.2f}%

🕒 Entry : {entry_time}

🕒 Exit : {ist}

{line()}
Capital Multiplier"""
            )

            delete_trade(symbol)

        else:

            send_telegram(
f"""{line()}

🔴 SELL EXECUTED

📈 Symbol : {symbol}

💰 Exit : ₹{price:.2f}

⚠ Entry Price Not Found

🕒 {ist}

{line()}
Capital Multiplier"""
            )

        return {
            "success": True
        }


    # ==========================================
    # REJECTED
    # ==========================================

    elif message == "rejected":

        send_telegram(
f"""{line()}

❌ ORDER REJECTED

📈 Symbol : {symbol}

Reason

{reason}

🕒 {ist}

{line()}
Capital Multiplier"""
        )

        return {
            "success": True
        }


    # ==========================================
    # CANCELLED
    # ==========================================

    elif message == "cancelled":

        send_telegram(
f"""{line()}

⚠ ORDER CANCELLED

📈 Symbol : {symbol}

🕒 {ist}

{line()}
Capital Multiplier"""
        )

        return {
            "success": True
        }


    # ==========================================
    # OTHER EVENTS
    # ==========================================

    print("=" * 50)
    print("IGNORED EVENT")
    print("=" * 50)

    print("Webhook Received :", current_time())

    print("Order ID         :", data.get("id"))
    print("Report Type      :", data.get("report_type"))
    print("Status           :", data.get("status"))
    print("Side             :", data.get("side"))
    print("Message          :", data.get("message"))
    print("Order Time       :", data.get("orderDateTime"))
    print("Update Time      :", data.get("orderUpdateTime"))
    print("Symbol           :", data.get("symbol"))

    print("Full Payload")
    print(data)

    print("=" * 50)

    return {
        "ignored": True
    }
