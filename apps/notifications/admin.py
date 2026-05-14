from django.contrib import admin

from apps.notifications.models import EmailLog
from apps.notifications.services import retry_email_log


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("id", "to_email", "subject", "template_key", "status", "created_at")
    list_filter = ("status", "template_key", "created_at")
    search_fields = ("to_email", "subject", "template_key", "error_message")
    ordering = ("-created_at",)
    readonly_fields = ("to_email", "subject", "template_key", "status", "error_message", "created_at")
    actions = ["retry_failed_emails"]

    def has_add_permission(self, request):
        return False

    @admin.action(description="Retry selected failed emails")
    def retry_failed_emails(self, request, queryset):
        failed_logs = queryset.filter(status=EmailLog.Status.FAILED)
        success_count = 0
        fail_count = 0
        for log in failed_logs:
            if retry_email_log(log):
                success_count += 1
            else:
                fail_count += 1
        self.message_user(
            request,
            f"Retry completed. Success: {success_count}, Failed: {fail_count}, Skipped: {queryset.count() - failed_logs.count()}",
        )
