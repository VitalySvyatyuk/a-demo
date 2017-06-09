from django.contrib import admin

from models import AccountGroup, SavedReport, IBSettings


class AccountGroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "account_count")
    readonly_fields = ("slug", )
    raw_id_fields = ('subpartner_user',)
    search_fields = ("_account_mt4_ids", )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ("slug", )
        return ("query", "slug")

    

class SavedReportAdmin(admin.ModelAdmin):
    list_display = ("name", "for_user", "filename", "creation_ts")
    search_fields = ("for_user__username", )
    readonly_fields = ("for_user", "creation_ts")


class IBSettingsAdmin(admin.ModelAdmin):
    list_display = ("ib_account", "reward_type", "cl_percent")
    search_fields = ("ib_account",)
    list_filter = ("reward_type",)


admin.site.register(AccountGroup, AccountGroupAdmin)
admin.site.register(SavedReport, SavedReportAdmin)
admin.site.register(IBSettings, IBSettingsAdmin)
