"""Customer data access — ported from the Kivy app's customer CSV functions."""

import csv
import os
from datetime import datetime

from .config import CUSTOMERS_FILE


def load_all_customers():
    customers = []
    if not os.path.isfile(CUSTOMERS_FILE):
        return customers
    try:
        with open(CUSTOMERS_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                customers.append(dict(row))
    except Exception as e:
        print(f"Error loading customers: {e}")
    return customers


def save_or_update_customer(customer_name, phone, delivery_area, street_address, order_amount):
    customers = load_all_customers()
    found = False
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for customer in customers:
        if customer["Phone Number"] == phone:
            customer["Customer Name"] = customer_name
            customer["Delivery Area"] = delivery_area
            customer["Street Address"] = street_address
            customer["Total Orders"] = str(int(customer["Total Orders"]) + 1)
            customer["Total Amount Spent"] = str(float(customer["Total Amount Spent"]) + float(order_amount))
            customer["Last Order Date"] = today
            found = True
            break

    if not found:
        customers.append({
            "Customer Name": customer_name,
            "Phone Number": phone,
            "Delivery Area": delivery_area,
            "Street Address": street_address,
            "Total Orders": "1",
            "Total Amount Spent": str(order_amount),
            "Last Order Date": today,
        })

    try:
        with open(CUSTOMERS_FILE, "w", newline="", encoding="utf-8") as file:
            fieldnames = [
                "Customer Name", "Phone Number", "Delivery Area",
                "Street Address", "Total Orders", "Total Amount Spent", "Last Order Date"
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for customer in customers:
                writer.writerow(customer)
    except Exception as e:
        print(f"Error saving customer updates: {e}")
