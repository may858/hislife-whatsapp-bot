"""Text-based sales & profit reports — ported from the Kivy dashboard screens,
returning strings instead of setting a Label widget, for use over WhatsApp."""

from datetime import datetime, timedelta

from .orders import load_all_orders
from .customers import load_all_customers
from .expenses import load_all_expenses
from .inventory import get_low_stock_items


def build_sales_dashboard_text():
    orders = load_all_orders()
    customers = load_all_customers()

    now = datetime.now()
    today = now.date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    today_orders = 0
    today_revenue = 0.0
    week_orders = 0
    week_revenue = 0.0
    month_orders = 0
    month_revenue = 0.0
    total_orders = 0
    total_revenue = 0.0

    product_qty = {}
    status_counts = {
        "Pending Payment": 0, "Paid": 0, "Processing": 0,
        "Out for Delivery": 0, "Delivered": 0, "Cancelled": 0,
    }

    for order in orders:
        total_orders += 1
        try:
            grand_total = float(order.get("Grand Total", 0) or 0)
        except ValueError:
            grand_total = 0.0
        total_revenue += grand_total

        order_date = None
        try:
            order_date = datetime.strptime(order.get("Timestamp", ""), "%Y-%m-%d %H:%M:%S").date()
        except (ValueError, TypeError):
            order_date = None

        if order_date == today:
            today_orders += 1
            today_revenue += grand_total
        if order_date and order_date >= week_start:
            week_orders += 1
            week_revenue += grand_total
        if order_date and order_date >= month_start:
            month_orders += 1
            month_revenue += grand_total

        product = order.get("Product", "")
        try:
            qty = int(order.get("Quantity", 0) or 0)
        except ValueError:
            qty = 0
        if product:
            product_qty[product] = product_qty.get(product, 0) + qty

        status = order.get("Status", "Pending Payment")
        status_counts[status] = status_counts.get(status, 0) + 1

    for customer in customers:
        try:
            customer["_spent"] = float(customer.get("Total Amount Spent", 0) or 0)
        except ValueError:
            customer["_spent"] = 0.0
    top_customers = sorted(customers, key=lambda c: c["_spent"], reverse=True)[:5]

    low_stock_items = get_low_stock_items(threshold=10)

    lines = [
        "*SALES OVERVIEW*",
        "────────────────────",
        f"Today's Orders: {today_orders}",
        f"Today's Revenue: ₦{today_revenue:,.0f}",
        "",
        f"This Week's Orders: {week_orders}",
        f"This Week's Revenue: ₦{week_revenue:,.0f}",
        "",
        f"This Month's Orders: {month_orders}",
        f"This Month's Revenue: ₦{month_revenue:,.0f}",
        "",
        f"Total Orders: {total_orders}",
        f"Total Revenue: ₦{total_revenue:,.0f}",
        "",
        "*PRODUCTS SOLD (Units)*",
        "────────────────────",
    ]
    for product, qty in product_qty.items():
        lines.append(f"{product}: {qty}")

    lines += ["", "*ORDER STATUS*", "────────────────────"]
    for status, count in status_counts.items():
        lines.append(f"{status}: {count}")

    lines += ["", "*TOP 5 CUSTOMERS*", "────────────────────"]
    if top_customers:
        for i, c in enumerate(top_customers, start=1):
            name = c.get("Customer Name", "Unknown")
            spent = c.get("_spent", 0)
            orders_count = c.get("Total Orders", "0")
            lines.append(f"{i}. {name} — ₦{spent:,.0f} ({orders_count} orders)")
    else:
        lines.append("No customer data yet.")

    lines += ["", "⚠️ *LOW STOCK (below 10)*", "────────────────────"]
    if low_stock_items:
        for product, size, stock in low_stock_items:
            lines.append(f"{product} ({size}): {stock} left")
    else:
        lines.append("All products sufficiently stocked.")

    return "\n".join(lines)


def build_profit_dashboard_text():
    orders = load_all_orders()
    expenses = load_all_expenses()

    now = datetime.now()
    today = now.date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    total_sales = today_sales = week_sales = month_sales = 0.0
    for order in orders:
        try:
            grand_total = float(order.get("Grand Total", 0) or 0)
        except ValueError:
            grand_total = 0.0
        total_sales += grand_total

        order_date = None
        try:
            order_date = datetime.strptime(order.get("Timestamp", ""), "%Y-%m-%d %H:%M:%S").date()
        except (ValueError, TypeError):
            order_date = None

        if order_date == today:
            today_sales += grand_total
        if order_date and order_date >= week_start:
            week_sales += grand_total
        if order_date and order_date >= month_start:
            month_sales += grand_total

    total_expenses = today_expenses = week_expenses = month_expenses = 0.0
    for expense in expenses:
        try:
            amount = float(expense.get("Amount", 0) or 0)
        except ValueError:
            amount = 0.0
        total_expenses += amount

        expense_date = None
        try:
            expense_date = datetime.strptime(expense.get("Date", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            expense_date = None

        if expense_date == today:
            today_expenses += amount
        if expense_date and expense_date >= week_start:
            week_expenses += amount
        if expense_date and expense_date >= month_start:
            month_expenses += amount

    net_profit = total_sales - total_expenses
    today_profit = today_sales - today_expenses
    week_profit = week_sales - week_expenses
    month_profit = month_sales - month_expenses

    lines = [
        "*PROFIT OVERVIEW*",
        "────────────────────",
        f"Total Sales: ₦{total_sales:,.0f}",
        f"Total Expenses: ₦{total_expenses:,.0f}",
        f"Net Profit: ₦{net_profit:,.0f}",
        "",
        f"Today's Profit: ₦{today_profit:,.0f}",
        f"This Week's Profit: ₦{week_profit:,.0f}",
        f"This Month's Profit: ₦{month_profit:,.0f}",
    ]
    return "\n".join(lines)
