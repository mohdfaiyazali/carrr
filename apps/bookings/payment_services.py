import hashlib
import hmac
from decimal import Decimal

from django.conf import settings


ADVANCE_PERCENT = Decimal("0.30")


def calculate_advance_amount(total_amount: Decimal) -> Decimal:
    return (total_amount * ADVANCE_PERCENT).quantize(Decimal("0.01"))


def calculate_cancellation_fee(booking) -> Decimal:
    return (booking.total_amount * Decimal("0.10")).quantize(Decimal("0.01"))


def create_razorpay_order(booking):
    amount_paise = int(booking.advance_amount * Decimal("100"))
    try:
        import razorpay

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({"amount": amount_paise, "currency": "INR", "payment_capture": 1})
        return order["id"], False
    except Exception:
        return f"mock_order_{booking.id}", True


def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
    if not secret:
        return True
    payload = f"{order_id}|{payment_id}".encode()
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
