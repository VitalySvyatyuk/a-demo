# -*- coding: utf-8 -*-

from django.contrib import admin
from platforms.mt4.external.models_users import ArchiveUser, RealUser, DemoUser
from platforms.models import ChangeQuote
from platforms.models import TradingAccount
from platforms.mt4.external.models_trade import RealTrade, DemoTrade, ArchiveTrade
from shared.admin import BaseAdmin, with_link


class TradingAccountAdmin(BaseAdmin):
    list_display = ("mt4_id", "user_with_link", "platform_type", "group_name", "is_deleted", "is_archived",
                    'deleted_comment', "creation_ts")
    list_filter = ("platform_type", "group_name", "is_deleted", "is_archived")
    search_fields = ("user__username", "user__first_name", "user__last_name",
                     "mt4_id", "group_name",)

    #exclude = ("user", )

    #readonly_fields = ("user_with_link", "mt4_id", "group_name")

    date_hierarchy = "creation_ts"

    user_with_link = with_link("user")
    registered_from_partner_domain_with_link = with_link("registered_from_partner_domain")
    actions = ['mark_deleted',]

    def mark_deleted(self, request, queryset):
        queryset.update(is_deleted=True)
    mark_deleted.short_description = u'Пометить как удаленные'  # type: ignore

admin.site.register(TradingAccount, TradingAccountAdmin)


class ChangeQuotesAdmin(admin.ModelAdmin):
    list_display = ('category', 'quotes')
    search_fields = ('quotes', )

admin.site.register(ChangeQuote, ChangeQuotesAdmin)

# Read only Mt4 models
class Mt4UserAdmin(admin.ModelAdmin):
    list_display = [f.name for f in RealUser._meta.fields]
    # Set every field as r/o to prevent in-place modifications
    readonly_fields = [f.name for f in RealUser._meta.fields]
    actions_selection_counter = False

    # Dont allow to manage it
    actions = None  # type: None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Same comments applies here
class Mt4TradeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in RealTrade._meta.fields]
    readonly_fields = [f.name for f in RealTrade._meta.fields]
    actions_selection_counter = False
    actions = None  # type: None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(RealUser, Mt4UserAdmin)
admin.site.register(DemoUser, Mt4UserAdmin)
admin.site.register(ArchiveUser, Mt4UserAdmin)

admin.site.register(RealTrade, Mt4TradeAdmin)
admin.site.register(DemoTrade, Mt4TradeAdmin)
admin.site.register(ArchiveTrade, Mt4TradeAdmin)


