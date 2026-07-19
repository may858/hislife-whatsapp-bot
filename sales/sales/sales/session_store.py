"""
Per-customer conversation state for the WhatsApp ordering flow.

WhatsApp webhook calls are stateless HTTP requests, so we need to remember
where each phone number is in the ordering conversation between messages.
Sessions are persisted to a JSON file on the data disk (DATA_DIR) so state
survives a gunicorn worker restart on Render, not just kept in memory.
"""

import json
import os
import threading

from .config import SESSIONS_FILE

_lock = threading.Lock()


def _load_all():
    if not os.path.isfile(SESSIONS_FILE):
        return {}
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Session store read error: {e}")
        return {}


def _save_all(data):
    try:
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Session store write error: {e}")


def get_session(phone_number):
    with _lock:
        data = _load_all()
        return data.get(phone_number, {"state": None})


def save_session(phone_number, session):
    with _lock:
        data = _load_all()
        data[phone_number] = session
        _save_all(data)


def clear_session(phone_number):
    with _lock:
        data = _load_all()
        if phone_number in data:
            del data[phone_number]
            _save_all(data)
