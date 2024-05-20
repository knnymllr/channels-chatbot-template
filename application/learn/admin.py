from django.contrib import admin
from .models import Learn_Message, Learn_Session
from django.contrib.admin.options import StackedInline  # Import StackedInline

# Register your models here.

class Learn_Message_Inline(StackedInline):  # Use StackedInline
    model = Learn_Message
    readonly_fields = ['message_id', 'session_id', 'date']  # Make these fields read-only
    fk_name = 'session_id'  # Foreign key name for Learn_Message

@admin.register(Learn_Session)
class Learn_Session_Admin(admin.ModelAdmin):
    inlines = [Learn_Message_Inline]  # Add the inline class
    list_filter = ['user_id']
