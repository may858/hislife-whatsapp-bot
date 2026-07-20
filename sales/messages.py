"""Message templates sent over WhatsApp — ported/adapted from the Kivy app."""


def build_admin_order_notification(order_id, name, phone, product, size, qty,
                                     area, address, instructions, total):
    return (
        f"🆕 *NEW ORDER — HIS LIFE AND PEACE FARMS*\n\n"
        f"*Order ID:* {order_id}\n"
        f"*Customer Name:* {name}\n"
        f"*Phone Number:* {phone}\n\n"
        f"*Product:* {product}\n"
        f"*Package Size:* {size}\n"
        f"*Quantity:* {qty}\n\n"
        f"*Delivery Area:* {area}\n"
        f"*Street Address:* {address}\n"
        f"*Special Instructions:* {instructions}\n\n"
        f"*Grand Total:* ₦{total:,}\n\n"
        f"Status: Pending Payment"
    )


def build_admin_payment_notification(order_id, name, phone, total):
    return (
        f"💰 *PAYMENT CLAIMED*\n\n"
        f"*Order ID:* {order_id}\n"
        f"*Customer:* {name}\n"
        f"*Phone:* {phone}\n"
        f"*Amount:* ₦{total:,}\n\n"
        f"Customer says payment has been made. Please verify and update status."
    )


def build_customer_receipt(order_id, order_date, order_time, name, product,
                            size, qty, product_total, delivery_fee, grand_total,
                            est_delivery_time):
    return (
        "════════════════════\n"
        "  HIS LIFE AND PEACE FARMS\n"
        "════════════════════\n\n"
        f"Order ID: {order_id}\n"
        f"Date: {order_date}  Time: {order_time}\n\n"
        f"Customer: {name}\n"
        f"Product: {product} ({size})\n"
        f"Quantity: {qty}\n\n"
        f"Product Total: ₦{product_total:,}\n"
        f"Delivery Fee: ₦{delivery_fee:,}\n"
        f"*Grand Total: ₦{grand_total:,}*\n\n"
        f"Estimated: {est_delivery_time}\n\n"
        "Payment Status: Pending Confirmation\n\n"
        "*Bank: Moniepoint*\n"
        "Account Name: Akintayo Mayowa Emmanuel\n"
        "Account Number: 7087171191\n\n"
        "Please transfer the exact amount, then reply *PAID* here once done.\n\n"
        "Thank you for choosing His Life and Peace Farms! 🌿"
    )
