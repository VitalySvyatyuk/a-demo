# coding: utf-8
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin

from models import Question, Category


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'answer': CKEditorWidget,
        }


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('question', 'answer', 'categories__name', 'priority')
    list_filter = ('categories', 'lang',)
    form = QuestionAdminForm


class CategoryAdmin(admin.ModelAdmin):
    list_filter = ('priority', 'lang', 'faq_version')
    list_display = ('__unicode__', 'priority', 'faq_version')
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Question, QuestionAdmin)
