import json
import os

TRADE_FILE = "trade_store.json"
WEBHOOK_FILE = "processed_webhooks.json"

MAX_WEBHOOKS = 1000


# ==========================================
# Create file if not exists
# ==========================================

def ensure_file(filename):

    if not os.path.exists(filename):

        with open(filename, "w") as f:
            json.dump({}, f)


# ==========================================
# Read JSON
# ==========================================

def read_json(filename):

    ensure_file(filename)

    with open(filename, "r") as f:

        try:
            return json.load(f)

        except:
            return {}


# ==========================================
# Write JSON
# ==========================================

def write_json(filename, data):

    with open(filename, "w") as f:

        json.dump(data, f, indent=4)


# ==========================================
# Save Entry
# ==========================================

def save_trade(symbol, entry_price, entry_time):

    data = read_json(TRADE_FILE)

    data[symbol] = {

        "entry": entry_price,

        "entry_time": entry_time

    }

    write_json(TRADE_FILE, data)


# ==========================================
# Get Entry
# ==========================================

def get_trade(symbol):

    data = read_json(TRADE_FILE)

    return data.get(symbol)


# ==========================================
# Delete Entry
# ==========================================

def delete_trade(symbol):

    data = read_json(TRADE_FILE)

    if symbol in data:

        del data[symbol]

        write_json(TRADE_FILE, data)


# ==========================================
# Duplicate Check
# ==========================================

def is_duplicate(order_id):

    data = read_json(WEBHOOK_FILE)

    if order_id in data:

        return True

    data[order_id] = True

    while len(data) > MAX_WEBHOOKS:

        first_key = next(iter(data))

        del data[first_key]

    write_json(WEBHOOK_FILE, data)

    return False
