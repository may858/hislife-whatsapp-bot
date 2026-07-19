"""Expense data access — ported from the Kivy app's expense CSV functions."""

import csv
import os

from .config import EXPENSES_FILE


def load_all_expenses():
    expenses = []
    if not os.path.isfile(EXPENSES_FILE):
        return expenses
    try:
        with open(EXPENSES_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                expenses.append(dict(row))
    except Exception as e:
        print(f"Error loading expenses: {e}")
    return expenses


def save_expense_to_csv(expense_id, date_str, category, description, amount):
    file_exists = os.path.isfile(EXPENSES_FILE)
    try:
        with open(EXPENSES_FILE, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Expense ID", "Date", "Category", "Description", "Amount"])
            writer.writerow([expense_id, date_str, category, description, amount])
    except Exception as e:
        print(f"Error saving expense: {e}")


def update_expense_in_csv(expense_id, date_str, category, description, amount):
    if not os.path.isfile(EXPENSES_FILE):
        return False
    rows = []
    fieldnames = ["Expense ID", "Date", "Category", "Description", "Amount"]
    updated = False
    try:
        with open(EXPENSES_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames or fieldnames
            for row in reader:
                if row.get("Expense ID") == expense_id:
                    row["Date"] = date_str
                    row["Category"] = category
                    row["Description"] = description
                    row["Amount"] = amount
                    updated = True
                rows.append(row)
        if updated:
            with open(EXPENSES_FILE, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        return updated
    except Exception as e:
        print(f"Error updating expense: {e}")
        return False


def delete_expense_from_csv(expense_id):
    if not os.path.isfile(EXPENSES_FILE):
        return False
    rows = []
    fieldnames = ["Expense ID", "Date", "Category", "Description", "Amount"]
    deleted = False
    try:
        with open(EXPENSES_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames or fieldnames
            for row in reader:
                if row.get("Expense ID") == expense_id:
                    deleted = True
                    continue
                rows.append(row)
        if deleted:
            with open(EXPENSES_FILE, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        return deleted
    except Exception as e:
        print(f"Error deleting expense: {e}")
        return False
