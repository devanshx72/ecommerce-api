import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_order_confirmation_email(
    user_email: str,
    username: str,
    order_id: int,
    total_amount: float,
    items: list,
    shipping_address: str
):
    """
    Send order confirmation email.
    Runs in background — not blocking the response.

    In production: use SendGrid, Mailgun, AWS SES
    For learning: we simulate sending (print to console)
    """

    # Build email content
    items_html = ""
    for item in items:
        items_html += f"""
        <tr>
            <td>{item['product_name']}</td>
            <td>{item['quantity']}</td>
            <td>₹{item['unit_price']:,.2f}</td>
            <td>₹{item['subtotal']:,.2f}</td>
        </tr>
        """

    html_body = f"""
    <html>
    <body>
        <h2>Order Confirmation — #{order_id}</h2>
        <p>Hi {username},</p>
        <p>Thank you for your order! Here are your order details:</p>

        <table border="1" cellpadding="8" cellspacing="0">
            <tr>
                <th>Product</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Subtotal</th>
            </tr>
            {items_html}
        </table>

        <h3>Total: ₹{total_amount:,.2f}</h3>
        <p><strong>Shipping to:</strong> {shipping_address}</p>

        <p>We will notify you when your order is shipped.</p>
        <p>Thank you for shopping with us!</p>
    </body>
    </html>
    """

    # ── Simulation mode ──
    # In production replace this with real SMTP
    # or email service (SendGrid, AWS SES etc)
    print("\n" + "="*50)
    print("📧 EMAIL SENT (Simulation)")
    print("="*50)
    print(f"To: {user_email}")
    print(f"Subject: Order Confirmation #{order_id}")
    print(f"Order Total: ₹{total_amount:,.2f}")
    print(f"Items: {len(items)}")
    print("="*50 + "\n")

    # ── Real SMTP (uncomment when you have credentials) ──
    # SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    # SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    # SMTP_USER = os.getenv("SMTP_USER")
    # SMTP_PASS = os.getenv("SMTP_PASS")
    #
    # msg = MIMEMultipart("alternative")
    # msg["Subject"] = f"Order Confirmation #{order_id}"
    # msg["From"] = SMTP_USER
    # msg["To"] = user_email
    # msg.attach(MIMEText(html_body, "html"))
    #
    # with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
    #     server.starttls()
    #     server.login(SMTP_USER, SMTP_PASS)
    #     server.sendmail(SMTP_USER, user_email, msg.as_string())


def send_status_update_email(
    user_email: str,
    username: str,
    order_id: int,
    new_status: str
):
    """Send email when order status changes."""
    status_messages = {
        "confirmed": "Your order has been confirmed and is being processed.",
        "shipped": "Great news! Your order has been shipped.",
        "delivered": "Your order has been delivered. Enjoy!",
        "cancelled": "Your order has been cancelled."
    }

    message = status_messages.get(new_status, f"Your order status: {new_status}")

    print("\n" + "="*50)
    print("📧 STATUS UPDATE EMAIL (Simulation)")
    print("="*50)
    print(f"To: {user_email}")
    print(f"Subject: Order #{order_id} — {new_status.upper()}")
    print(f"Message: {message}")
    print("="*50 + "\n")