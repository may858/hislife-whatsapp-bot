"""Inventory data access — ported from the Kivy app's inventory functions."""

import csv
import os

from .config import INVENTORY_FILE


def create_inventory_file():
    if os.path.isfile(INVENTORY_FILE):
        return
    try:
        with open(INVENTORY_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["Product", "Package Size", "Price", "Stock"])
            writer.writerow(["Honey", "250ml", 2500, 100])
            writer.writerow(["Honey", "500ml", 5000, 80])
            writer.writerow(["Honey", "1 Litre", 10000, 50])
            writer.writerow(["BSF Larvae", "1kg", 3500, 200])
            writer.writerow(["Catfish", "1kg", 2500, 100])
        print("Inventory file created successfully.")
    except Exception as e:
        print(f"Error creating inventory file: {e}")


def get_products():
    products = []
    if not os.path.isfile(INVENTORY_FILE):
        return products
    with open(INVENTORY_FILE, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            product = row["Product"]
            if product not in products:
                products.append(product)
    return products


def get_product_details(product_name):
    items = []
    if not os.path.isfile(INVENTORY_FILE):
        return items
    try:
        with open(INVENTORY_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row or row.get("Product") != product_name:
                    continue
                size = (row.get("Package Size") or "").strip()
                price_raw = (row.get("Price") or "").strip()
                stock_raw = (row.get("Stock") or "").strip()
                if not size or not price_raw or not stock_raw:
                    continue
                try:
                    price = int(float(price_raw))
                    stock = int(float(stock_raw))
                except (ValueError, TypeError):
                    continue
                items.append({"size": size, "price": price, "stock": stock})
    except Exception as e:
        print(f"Inventory Error in get_product_details: {e}")
    return items


def get_stock(product, package_size):
    if not os.path.isfile(INVENTORY_FILE):
        return 0
    try:
        with open(INVENTORY_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Product"] == product and row["Package Size"] == package_size:
                    return int(row["Stock"])
    except Exception as e:
        print(f"Inventory Error: {e}")
    return 0


def reduce_stock(product, package_size, quantity):
    if not os.path.isfile(INVENTORY_FILE):
        return False
    rows = []
    try:
        with open(INVENTORY_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Product"] == product and row["Package Size"] == package_size:
                    current_stock = int(row["Stock"])
                    if current_stock < quantity:
                        return False
                    row["Stock"] = str(current_stock - quantity)
                rows.append(row)

        with open(INVENTORY_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=["Product", "Package Size", "Price", "Stock"])
            writer.writeheader()
            writer.writerows(rows)
        return True
    except Exception as e:
        print(f"Inventory Error: {e}")
        return False


def delete_product_from_inventory(product_name):
    if not os.path.isfile(INVENTORY_FILE):
        return False
    rows = []
    item_found = False
    target_name = product_name.strip().lower()
    try:
        with open(INVENTORY_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Product"].strip().lower() == target_name:
                    item_found = True
                else:
                    rows.append(row)

        if item_found:
            with open(INVENTORY_FILE, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.DictWriter(file, fieldnames=["Product", "Package Size", "Price", "Stock"])
                writer.writeheader()
                writer.writerows(rows)
            return True
        return False
    except Exception as e:
        print(f"Delete Error: {e}")
        return False


def add_product(product_name, package_size, price, stock):
    """Add a new product/size row. Returns (success: bool, message: str)."""
    if not product_name or not package_size:
        return False, "Product name and package size are required."
    create_inventory_file()

    try:
        with open(INVENTORY_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (row["Product"].strip().lower() == product_name.strip().lower()
                        and row["Package Size"].strip().lower() == package_size.strip().lower()):
                    return False, f"'{product_name} ({package_size})' already exists in inventory."
    except Exception as e:
        return False, f"Error checking inventory: {e}"

    try:
        with open(INVENTORY_FILE, "a", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow([product_name, package_size, price, stock])
        return True, f"Product '{product_name} ({package_size})' added successfully."
    except Exception as e:
        return False, f"Error adding product: {e}"


def get_low_stock_items(threshold=10):
    low_stock = []
    if not os.path.isfile(INVENTORY_FILE):
        return low_stock
    try:
        with open(INVENTORY_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    stock = int(row.get("Stock", 0))
                except ValueError:
                    stock = 0
                if stock < threshold:
                    low_stock.append((row.get("Product", "N/A"), row.get("Package Size", "N/A"), stock))
    except Exception as e:
        print(f"Inventory Error: {e}")
    return low_stock
