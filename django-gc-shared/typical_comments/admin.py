# -*- coding: utf-8 -*-

from django.contrib import admin

from models import TypicalComment, TypicalCommentsCategory
from shared.admin import BaseAdmin


class TypicalCommentAdmin(BaseAdmin):
    list_display = ("text", "category")
    list_filter = ("category", )


class TypicalCommentsCategoryAdmin(BaseAdmin):
    list_display = ("name", )


# admin.site.register(TypicalComment, TypicalCommentAdmin)
# admin.site.register(TypicalCommentsCategory, TypicalCommentsCategoryAdmin)
# Vasya said unnecessary
