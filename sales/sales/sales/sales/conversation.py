"""
Conversation engine: takes an incoming WhatsApp text message + the sender's
phone number, advances that phone number's saved session state, performs
any needed side effects (saving orders, reducing stock, etc.), and returns
the reply text to send back plus an optional admin-notification text.

This replaces the Kivy screens' interactive flow with a text-based one,
since Kivy's GUI can't run on a headless Render web service.
"""

from datetime import datetime

from . import inventory, orders, customers, reports
from .config import DELIVERY_FEES, EXPENSE_CATEGORIES, ADMIN_PASSWORD
from .expenses import save_expense_to_csv
from .messages import (
    build_admin_order_notification,
    build_admin_payment_notification,
    build_customer_receipt,
)
from .session_store import get_session, save_session, clear_session

MAIN_MENU_TEXT = (
    "Welcome to *His Life and Peace Farms* 🐟🍯🐛\n\n"
    "Reply with a number:\n"
    "1️⃣ Place an Order\n"
    "2️⃣ Track an Order\n"
    "3️⃣ Our Products\n"
    "4️⃣ Contact Us\n"
    "5️⃣ Admin"
)

PRODUCTS_INFO_TEXT = (
    "🍯 100% Pure Natural Honey\n"
    "🐟 Fresh Catfish\n"
    "🐛 Black Soldier Fly (BSF) Larvae\n\n"
    "Reply 'menu' to go back."
)

CONTACT_US_TEXT = (
    "*His Life and Peace Farms*\n"
    "📞 07087171191\n"
    "📍 Ibadan, Oyo State, Nigeria\n\n"
    "Reply 'menu' to go back."
)


def _numbered_list(items):
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, start=1))


def _reset(phone, text=MAIN_MENU_TEXT):
    clear_session(phone)
    save_session(phone, {"state": "MAIN_MENU"})
    return text


def handle_message(phone_number, text):
    """
    Returns a tuple: (reply_to_customer, admin_notification_or_None)
    """
    raw = (text or "").strip()
    lowered = raw.lower()
    session = get_session(phone_number)
    state = session.get("state")

    # Global commands available from anywhere
    if lowered in ("menu", "hi", "hello", "start"):
        return _reset(phone_number), None
    if lowered == "cancel":
        return _reset(phone_number, "Cancelled. " + MAIN_MENU_TEXT), None

    # ---------------- Entry point ----------------
    if state is None:
        session["state"] = "MAIN_MENU"
        save_session(phone_number, session)
        return MAIN_MENU_TEXT, None

    # ---------------- Main menu ----------------
    if state == "MAIN_MENU":
        if raw == "1":
            products = inventory.get_products()
            if not products:
                return "Sorry, no products are available right now. Please try later.", None
            session["state"] = "PRODUCT_CHOICE"
            session["products"] = products
            save_session(phone_number, session)
            return "Which product would you like to order?\n\n" + _numbered_list(products), None
        if raw == "2":
            session["state"] = "TRACK_ORDER"
            save_session(phone_number, session)
            return "Please enter your Order ID (e.g. HLP-20260719-12345):", None
        if raw == "3":
            return PRODUCTS_INFO_TEXT, None
        if raw == "4":
            return CONTACT_US_TEXT, None
        if raw == "5":
            session["state"] = "ADMIN_AUTH"
            save_session(phone_number, session)
            return "🔒 Enter admin password:", None
        return "Sorry, I didn't understand that.\n\n" + MAIN_MENU_TEXT, None

    # ---------------- Ordering flow ----------------
    if state == "PRODUCT_CHOICE":
        products = session.get("products", [])
        idx = _to_index(raw, len(products))
        if idx is None:
            return "Please reply with a valid number from the list, or 'menu' to start over.", None
        product = products[idx]
        options = inventory.get_product_details(product)
        if not options:
            return _reset(phone_number, f"Sorry, '{product}' is currently unavailable.\n\n" + MAIN_MENU_TEXT), None
        session["state"] = "SIZE_CHOICE"
        session["product"] = product
        session["size_options"] = options
        save_session(phone_number, session)
        lines = [f"{i}. {o['size']} — ₦{o['price']:,}" for i, o in enumerate(options, start=1)]
        return f"Select a package size for {product}:\n\n" + "\n".join(lines), None

    if state == "SIZE_CHOICE":
        options = session.get("size_options", [])
        idx = _to_index(raw, len(options))
        if idx is None:
            return "Please reply with a valid number, or 'menu' to start over.", None
        chosen = options[idx]
        session["state"] = "QTY"
        session["size"] = chosen["size"]
        session["unit_price"] = chosen["price"]
        save_session(phone_number, session)
        return "How many units would you like? (reply with a number)", None

    if state == "QTY":
        if not raw.isdigit() or int(raw) <= 0:
            return "Please enter a valid quantity (whole number greater than 0).", None
        qty = int(raw)
        stock = inventory.get_stock(session["product"], session["size"])
        if qty > stock:
            return f"Sorry, only {stock} left in stock for that size. Please enter a smaller quantity.", None
        session["quantity"] = qty
        session["state"] = "NAME"
        save_session(phone_number, session)
        return "What name should we put on the order?", None

    if state == "NAME":
        if not raw:
            return "Please enter your name.", None
        session["customer_name"] = raw
        session["state"] = "DELIVERY_AREA"
        save_session(phone_number, session)
        areas = list(DELIVERY_FEES.keys())
        session["areas"] = areas
        save_session(phone_number, session)
        lines = [f"{i}. {a} (₦{DELIVERY_FEES[a]:,})" for i, a in enumerate(areas, start=1)]
        return "Select your delivery area:\n\n" + "\n".join(lines), None

    if state == "DELIVERY_AREA":
        areas = session.get("areas", list(DELIVERY_FEES.keys()))
        idx = _to_index(raw, len(areas))
        if idx is None:
            return "Please reply with a valid number from the list.", None
        area = areas[idx]
        session["delivery_area"] = area
        session["delivery_fee"] = DELIVERY_FEES[area]
        if area == "Store Pickup (No Delivery)":
            session["street_address"] = "N/A"
            session["state"] = "INSTRUCTIONS"
            save_session(phone_number, session)
            return "Any special instructions? (reply your note, or 'skip')", None
        session["state"] = "ADDRESS"
        save_session(phone_number, session)
        return "Please enter your street address:", None

    if state == "ADDRESS":
        if not raw:
            return "Please enter a valid street address.", None
        session["street_address"] = raw
        session["state"] = "INSTRUCTIONS"
        save_session(phone_number, session)
        return "Any special instructions? (reply your note, or 'skip')", None

    if state == "INSTRUCTIONS":
        session["special_instructions"] = "None" if lowered == "skip" else raw
        session["state"] = "CONFIRM"
        summary_text = _build_order_summary(session)  # mutates session with totals
        save_session(phone_number, session)
        return summary_text + "\n\nReply *YES* to confirm or *NO* to cancel.", None

    if state == "CONFIRM":
        if lowered in ("yes", "y"):
            return _finalize_order(phone_number, session)
        if lowered in ("no", "n"):
            return _reset(phone_number, "Order cancelled.\n\n" + MAIN_MENU_TEXT), None
        return "Please reply *YES* to confirm or *NO* to cancel.", None

    if state == "AWAITING_PAYMENT":
        if lowered == "paid":
            order_id = session.get("last_order_id")
            name = session.get("customer_name", "")
            total = session.get("grand_total", 0)
            admin_msg = build_admin_payment_notification(order_id, name, phone_number, total)
            return _reset(
                phone_number,
                "Thanks! We've been notified and will confirm your payment shortly. 🙏\n\n" + MAIN_MENU_TEXT
            ), admin_msg
        return "Once you've made the transfer, reply *PAID* so we can confirm it.", None

    # ---------------- Order tracking ----------------
    if state == "TRACK_ORDER":
        order = orders.get_order_by_id(raw)
        if not order:
            return _reset(phone_number, "No order found with that ID.\n\n" + MAIN_MENU_TEXT), None
        reply = (
            f"Order {order.get('Order ID')}\n"
            f"Product: {order.get('Product')} ({order.get('Package Size')})\n"
            f"Quantity: {order.get('Quantity')}\n"
            f"Grand Total: ₦{order.get('Grand Total')}\n"
            f"Status: {order.get('Status')}\n"
            f"Estimated: {order.get('Estimated Delivery Time')}"
        )
        return _reset(phone_number, reply + "\n\n" + MAIN_MENU_TEXT), None

    # ---------------- Admin flow ----------------
    if state == "ADMIN_AUTH":
        if raw == ADMIN_PASSWORD:
            session["state"] = "ADMIN_MENU"
            save_session(phone_number, session)
            return _admin_menu_text(), None
        return _reset(phone_number, "Incorrect password.\n\n" + MAIN_MENU_TEXT), None

    if state == "ADMIN_MENU":
        if raw == "1":
            return _reset(phone_number, reports.build_sales_dashboard_text() + "\n\n" + MAIN_MENU_TEXT), None
        if raw == "2":
            return _reset(phone_number, reports.build_profit_dashboard_text() + "\n\n" + MAIN_MENU_TEXT), None
        if raw == "3":
            low = inventory.get_low_stock_items(threshold=10)
            if not low:
                text = "All products sufficiently stocked."
            else:
                text = "\n".join(f"{p} ({s}): {q} left" for p, s, q in low)
            return _reset(phone_number, text + "\n\n" + MAIN_MENU_TEXT), None
        if raw == "4":
            session["state"] = "ADMIN_EXPENSE_CATEGORY"
            save_session(phone_number, session)
            return "Select expense category:\n\n" + _numbered_list(EXPENSE_CATEGORIES), None
        if raw == "5":
            return _reset(phone_number, MAIN_MENU_TEXT), None
        return "Please choose a valid option.\n\n" + _admin_menu_text(), None

    if state == "ADMIN_EXPENSE_CATEGORY":
        idx = _to_index(raw, len(EXPENSE_CATEGORIES))
        if idx is None:
            return "Please choose a valid category number.", None
        session["expense_category"] = EXPENSE_CATEGORIES[idx]
        session["state"] = "ADMIN_EXPENSE_DESCRIPTION"
        save_session(phone_number, session)
        return "Enter a short description for this expense:", None

    if state == "ADMIN_EXPENSE_DESCRIPTION":
        if not raw:
            return "Please enter a description.", None
        session["expense_description"] = raw
        session["state"] = "ADMIN_EXPENSE_AMOUNT"
        save_session(phone_number, session)
        return "Enter the amount (numbers only):", None

    if state == "ADMIN_EXPENSE_AMOUNT":
        try:
            amount = float(raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            return "Please enter a valid positive amount.", None
        expense_id = f"EXP-{datetime.now().strftime('%Y%m%d')}-{__import__('random').randint(10000, 99999)}"
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_expense_to_csv(expense_id, date_str, session["expense_category"],
                             session["expense_description"], amount)
        return _reset(phone_number, "✅ Expense saved.\n\n" + MAIN_MENU_TEXT), None

    # Fallback — unknown state, reset
    return _reset(phone_number), None


def _to_index(raw, length):
    if not raw.isdigit():
        return None
    idx = int(raw) - 1
    if 0 <= idx < length:
        return idx
    return None


def _admin_menu_text():
    return (
        "*Admin Menu*\n\n"
        "1. Sales Dashboard\n"
        "2. Profit Dashboard\n"
        "3. Low Stock Check\n"
        "4. Add Expense\n"
        "5. Exit"
    )


def _build_order_summary(session):
    product_total = session["unit_price"] * session["quantity"]
    delivery_fee = session["delivery_fee"]
    grand_total = product_total + delivery_fee
    session["product_total"] = product_total
    session["grand_total"] = grand_total
    return (
        "*Order Summary*\n"
        f"Name: {session['customer_name']}\n"
        f"Product: {session['product']} ({session['size']})\n"
        f"Quantity: {session['quantity']}\n"
        f"Delivery Area: {session['delivery_area']}\n"
        f"Address: {session.get('street_address', 'N/A')}\n"
        f"Instructions: {session.get('special_instructions', 'None')}\n\n"
        f"Product Total: ₦{product_total:,}\n"
        f"Delivery Fee: ₦{delivery_fee:,}\n"
        f"*Grand Total: ₦{grand_total:,}*"
    )


def _finalize_order(phone_number, session):
    product = session["product"]
    size = session["size"]
    qty = session["quantity"]

    if not inventory.reduce_stock(product, size, qty):
        return _reset(
            phone_number,
            "Sorry, this item just went out of stock. Please choose another option.\n\n" + MAIN_MENU_TEXT
        ), None

    order_id = orders.generate_order_id()
    now = datetime.now()
    area = session["delivery_area"]
    est = ("Ready for pickup within 1 hour after confirmation."
           if area == "Store Pickup (No Delivery)"
           else "Estimated delivery: 24–48 hours after confirmation.")

    orders.save_order_to_csv(
        order_id, session["customer_name"], phone_number, area,
        session.get("street_address", "N/A"), session.get("special_instructions", "None"),
        product, size, session["unit_price"], qty, session["product_total"],
        session["delivery_fee"], session["grand_total"], est
    )
    customers.save_or_update_customer(
        session["customer_name"], phone_number, area,
        session.get("street_address", "N/A"), session["grand_total"]
    )

    receipt = build_customer_receipt(
        order_id, now.strftime("%d-%b-%Y"), now.strftime("%I:%M %p"),
        session["customer_name"], product, size, qty, session["product_total"],
        session["delivery_fee"], session["grand_total"], est
    )
    admin_notification = build_admin_order_notification(
        order_id, session["customer_name"], phone_number, product, size, qty,
        area, session.get("street_address", "N/A"), session.get("special_instructions", "None"),
        session["grand_total"]
    )

    session["state"] = "AWAITING_PAYMENT"
    session["last_order_id"] = order_id
    save_session(phone_number, session)

    return receipt, admin_notification
