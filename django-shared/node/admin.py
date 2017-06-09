from django.contrib import admin
from django import forms

from models import *
from ckeditor.widgets import CKEditorWidget


class CKEditorAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget())


class NodeAdmin(admin.ModelAdmin):
    form = CKEditorAdminForm
    list_display = ('title', 'content_type', 'url_alias', 'creation_ts', 'author', 'language', 'update_ts')
    search_fields = ('title', 'url_alias')
    list_filter = ('language',)

    save_as = True

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        obj.save()


class PageAdmin(NodeAdmin):
    list_display = ('title', 'content_type', 'url_alias', 'language', 'published', 'creation_ts', 'update_ts', 'author')
    list_filter = ('creation_ts', 'language', 'published')

    save_as = True


admin.site.register(Page, PageAdmin)
admin.site.register(LoggedInUserPage, PageAdmin)