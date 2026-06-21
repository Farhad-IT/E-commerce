import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_order_email(email: str, order_id: int) -> dict:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Order #{order_id} confirmed"
    msg["From"] = f"My Shop <{SMTP_USER}>"
    msg["To"] = email

    html_body = f"""
    <html>
    <body>
    <h2>Thank you for your order!</h2>
    <p>Your order number: <b>#{order_id}.</b></p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return {"status": "sent", "email": email, "order_id": order_id}
    except smtplib.SMTPException as e:
        raise RuntimeError(f"Error sending email to {email}: {e}")


def send_welcome_email(email: str, name: str) -> dict:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Welcome {name}!"
    msg["From"] = f"My Shop <{SMTP_USER}>"
    msg["To"] = email

    text_body = f"""
    <html>
    <body>
    <h2>We welcome you <b>#{name}</b></h2>!
    <p>We hope you enjoy our website.</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(text_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return {"status": "sent", "email": email, "username": name}
    except smtplib.SMTPException as e:
        raise RuntimeError(f"Error sending email to {email}: {e}")


def send_abandoned_cart_email(email: str, cart_id: int):

    msg = MIMEMultipart("alternative")

    msg["Subject"] = "You left items in your cart"
    msg["From"] = SMTP_USER
    msg["To"] = email

    text_body = f"""
    You have items waiting in your cart.

    Cart number: #{cart_id}

    Come back and complete your order!
    """

    msg.attach(MIMEText(text_body, "plain"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return True

    except smtplib.SMTPException as e:
        raise RuntimeError(f"Error sending abandoned cart email: {e}")
