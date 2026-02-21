from django.contrib import admin
from .models import ScannedResume

@admin.register(ScannedResume)
class ScannedResumeAdmin(admin.ModelAdmin):
    list_display = ('filename', 'score', 'uploaded_at')
    list_filter = ('uploaded_at',)
    readonly_fields = ('uploaded_at',)