"""Order data access — ported from the Kivy app's order CSV functions."""

import csv
import os
import random
from datetime import datetime

from .config import ORDERS_FILE


def generate_order_id():
    date_str = datetime.now().strftime("%Y%m%d")
    return f"HLP-{date_str}-{random.randint(10000, 99999)}"


def load_all_orders():
    orders = []
    if not os.path.isfile(ORDERS_FILE):
        return orders
    try:
        with open(ORDERS_FILE, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                orders.append(dict(row))
    except Exception as e:
        print(f"Error loading orders: {e}")
    return orders


def get_order_by_id(order_id):
    for order in load_all_orders():
        if order.get("Order ID", "").strip().lower() == order_id.strip().lower():
            return order
    return None


def update_order_status_in_csv(order_id, new_status):
    if not os.path.isfile(ORDERS_FILE):
        return False
    rows = []
    headers = []
    updated = False
    try:
        with open(ORDERS_FILE, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)
            status_idx = headers.index("Status") if "Status" in headers else 15
            id_idx = headers.index("Order ID") if "Order ID" in headers else 1

            for row in reader:
                if len(row) > id_idx and row[id_idx] == order_id:
                    if len(row) > status_idx:
                        row[status_idx] = new_status
                    updated = True
                rows.append(row)

        if updated:
            with open(ORDERS_FILE, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            return True
    except Exception as e:
        print(f"Error updating order row status: {e}")
    return False


def save_order_to_csv(order_id, customer, phone, delivery_area, street_address,
                       special_instructions, product, size, unit_price, qty,
                       product_total, delivery_fee, grand_total, est_delivery_time):
    file_exists = os.path.isfile(ORDERS_FILE)
    try:
        with open(ORDERS_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow([
                    "Timestamp", "Order ID", "Customer Name", "Phone Number",
                    "Delivery Area", "Street Address", "Special Instructions", "Product", "Package Size",
                    "Unit Price", "Quantity", "Product Total", "Delivery Fee", "Grand Total",
                    "Estimated Delivery Time", "Status"
                ])
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([
                timestamp, order_id, customer, phone,
                delivery_area, street_address, special_instructions, product, size,
                unit_price, qty, product_total, delivery_fee, grand_total, est_delivery_time,
                "Pending Payment"
            ])
    except Exception as e:
        print(f"Error saving order: {e}")
