from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.notifications.models import EmailLog
from apps.users.models import User


def _send_logged_email(to_email, subject, template_key, context):
    if not to_email:
        return
    try:
        text_body = render_to_string(f"emails/{template_key}.txt", context)
        message = EmailMultiAlternatives(
            subject=subject,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@carz.local"),
            to=[to_email],
            body=text_body,
        )
        try:
            html_body = render_to_string(f"emails/{template_key}.html", context)
            message.attach_alternative(html_body, "text/html")
        except Exception:
            pass
        message.send(fail_silently=False)
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
    context = {"booking": booking, "customer": booking.customer, "car": booking.car}
    _send_logged_email(
        booking.customer.email,
        "Booking created",
        "booking_created_customer",
        context,
    )


def notify_customer_booking_status_changed(booking):
    context = {"booking": booking, "customer": booking.customer, "car": booking.car}
    _send_logged_email(
        booking.customer.email,
        f"Booking #{booking.id} status updated",
        "booking_status_customer",
        context,
    )


def notify_managers_booking_alert(booking, action="created"):
    managers = User.objects.filter(role__in=[User.Role.MANAGER, User.Role.ADMIN], is_active=True).exclude(email="")
    subject = f"Booking #{booking.id} {action}"
    context = {"booking": booking, "action": action, "customer": booking.customer, "car": booking.car}
    for manager in managers:
        _send_logged_email(manager.email, subject, "booking_manager_alert", context)
