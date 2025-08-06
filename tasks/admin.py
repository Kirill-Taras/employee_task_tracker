from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "executor", "status", "due_date")
    list_filter = ("status", "due_date")
    search_fields = ("title", "executor__full_name")
