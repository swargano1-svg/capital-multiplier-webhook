from fastapi import FastAPI, Request
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from storage import save_trade, get_trade, delete_trade, is_duplicate

app = FastAPI(title="Capital Multiplier V3")

IST = ZoneInfo("Asia/Kolkata")

BOT_TOKEN = os.getenv("BOT_TOKEN", "demo_token")


# =========================
# HELPERS
# =========================
def get_time():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def validate(data):
    try:
        return (
            data["symbol"]
            and data["signal"] in ["BUY", "SELL", "EXIT"]
            and float(data["price"]) > 0
            and data["order_id"]
        )
    except:
        return False


def verify_token(data):
    return data.get("token") == BOT_TOKEN


# =========================
# CORE ENGINE
# =========================
def process(data):
    symbol = data["symbol"]
    signal = data["signal"]
    price = float(data["price"])
    order_id = data["order_id"]

    # duplicate check
    if is_duplicate(order_id):
        return {"status": "DUPLICATE_IGNORED"}

    # ENTRY
    if signal in ["BUY", "SELL"]:
        if get_trade(symbol):
            return {"status": "ALREADY_IN_POSITION"}

        save_trade(symbol, price, get_time())

        return {
            "status": "ENTERED",
            "symbol": symbol,
            "price": price
        }

    # EXIT
    if signal == "EXIT":
        trade = get_trade(symbol)

        if not trade:
            return {"status": "NO_POSITION_FOUND"}

        entry = trade["entry"]
        entry_time = trade["entry_time"]

        pnl = price - entry if signal == "EXIT" else 0

        if signal == "SELL":
            pnl = entry - price

        delete_trade(symbol)

        return {
            "status": "EXITED",
            "symbol": symbol,
            "entry": entry,
            "exit": price,
            "pnl": round(pnl, 2),
            "entry_time": entry_time,
            "exit_time": get_time()
        }

    return {"status": "NO_ACTION"}


# =========================
# WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    if not verify_token(data):
        return {"error": "Unauthorized"}

    if not validate(data):
        return {"error": "Invalid payload"}

    return process(data)


# =========================
# HEALTH
# =========================
@app.get("/")
def home():
    return {"status": "Capital Multiplier V3 Running"}
