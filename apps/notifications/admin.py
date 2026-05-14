from django.contrib import admin

from apps.notifications.models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("id", "to_email", "subject", "template_key", "status", "created_at")
    list_filter = ("status", "template_key", "created_at")
    search_fields = ("to_email", "subject", "template_key", "error_message")
    ordering = ("-created_at",)
    readonly_fields = ("to_email", "subject", "template_key", "status", "error_message", "created_at")

    def has_add_permission(self, request):
        return False
