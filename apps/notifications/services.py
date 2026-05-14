from django.conf import settings
from django.core.mail import send_mail

from apps.notifications.models import EmailLog
from apps.users.models import User


def _send_logged_email(to_email, subject, message, template_key):
    if not to_email:
        return
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@carz.local"),
            recipient_list=[to_email],
            fail_silently=False,
        )
        EmailLog.objects.create(to_email=to_email, subject=subject, template_key=template_key, status=EmailLog.Status.SENT)
    except Exception as exc:
        EmailLog.objects.create(
            to_email=to_email,
            subject=subject,
            template_key=template_key,
            status=EmailLog.Status.FAILED,
            error_message=str(exc),
        )


def notify_customer_booking_created(booking):
    _send_logged_email(
        booking.customer.email,
        "Booking created",
        f"Your booking #{booking.id} was created successfully.",
        "booking_created_customer",
    )


def notify_customer_booking_status_changed(booking):
    _send_logged_email(
        booking.customer.email,
        f"Booking #{booking.id} status updated",
        f"Your booking status is now: {booking.status}.",
        "booking_status_customer",
    )


def notify_managers_booking_alert(booking, action="created"):
    managers = User.objects.filter(role__in=[User.Role.MANAGER, User.Role.ADMIN], is_active=True).exclude(email="")
    subject = f"Booking #{booking.id} {action}"
    message = f"Booking #{booking.id} for {booking.car} is now {booking.status}."
    for manager in managers:
        _send_logged_email(manager.email, subject, message, f"booking_{action}_manager")
