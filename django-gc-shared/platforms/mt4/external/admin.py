from django.contrib import admin

from .models import ChangeIssue


class ChangeIssueAdmin(admin.ModelAdmin):
    list_display = ('login', 'field', 'value', 'status', 'creation_ts')
    readonly_fields = ('login', 'field', 'value', 'status', 'creation_ts')
    search_fields = ('login', 'status')


admin.site.register(ChangeIssue, ChangeIssueAdmin)
