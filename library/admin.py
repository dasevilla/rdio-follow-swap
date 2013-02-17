from django.contrib import admin

from library.models import RdioConnection


class RdioConnectionAdmin(admin.ModelAdmin):
    fields = ('follower', 'followee', 'status')
    readonly_fields = ()
    list_display = ('follower', 'followee', 'status')
    list_filter = ('status',)
    radio_fields = {
        'status': admin.VERTICAL,
    }


admin.site.register(RdioConnection, RdioConnectionAdmin)
