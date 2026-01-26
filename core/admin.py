from django.contrib import admin
from .models import Woman, Section, Issue, Appearance, IssueCover

class IssueCoverInline(admin.TabularInline):
    model = IssueCover
    extra = 1

class IssueAdmin(admin.ModelAdmin):
    inlines = [IssueCoverInline]
    ordering = ['publishing_date']

admin.site.register(Woman)
admin.site.register(Section)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Appearance)
