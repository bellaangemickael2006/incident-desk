from django.contrib import admin
from .models import AuditEvent, Comment, Incident


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ["reference", "title", "severity", "status", "created_by", "assigned_to", "created_at"]
    list_select_related = ["created_by", "assigned_to"]
    list_filter = ["severity", "status"]
    search_fields = ["title", "created_by__username", "assigned_to__username"]
    readonly_fields = ["created_by", "created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["pk", "incident", "author", "created_at"]
    list_select_related = ["incident", "author"]
    readonly_fields = ["incident", "author", "created_at"]


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ["created_at", "actor", "verb", "incident", "detail"]
    list_select_related = ["actor", "incident"]
    readonly_fields = ["incident", "actor", "verb", "detail", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
