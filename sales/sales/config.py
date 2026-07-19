"""
Central configuration for the sales management modules.

DATA_DIR controls where all CSV/JSON data files live.
On Render, set the environment variable DATA_DIR to the mount path of your
persistent disk (e.g. /var/data). If DATA_DIR is not set, it falls back to
a local ./data folder next to this file (fine for local testing, but NOT
persistent across Render deploys/restarts on the free/local-disk tier).
"""

import os

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data"
))
os.makedirs(DATA_DIR, exist_ok=True)

ORDERS_FILE = os.path.join(DATA_DIR, "orders.csv")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.csv")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.csv")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.csv")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")

DELIVERY_FEES = {
    "Store Pickup (No Delivery)": 0,
    "Iyana Agbala / New Ife Road": 500,
    "Iwo Road": 1000,
    "Challenge": 1500,
    "Dugbe": 1500,
    "Mokola": 1500,
    "Bodija": 1500,
    "Akobo": 2000,
    "Moniya": 2000,
    "Other (Ibadan)": 2500,
}

EXPENSE_CATEGORIES = [
    "Feed", "Transport", "Fuel", "Labour",
    "Equipment", "Maintenance", "Utilities", "Other",
]

BUSINESS_WHATSAPP_NUMBER = os.environ.get("BUSINESS_WHATSAPP_NUMBER", "2347087171191")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "HLP2026")
