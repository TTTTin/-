from django.contrib import admin

# Register your models here.


from production_process.models import Production_prosess,Production_listforaddblock,Production_listfordelblock


class ProcessAdmin(admin.ModelAdmin):
    search_fields = ('production_id',)
    list_display = ('production_id', 'listforaddblock', 'listfordelblock', 'listforBackdrop','listforChange','listforChangeOp','listforCostume','listfordelbac','listfordelcos','listfordelspr','listforDoubleclickBlock','listforSound','listforSpr','listfordelsnd')
    # list_display = ('production_id', 'listforaddblock')

    class Meta:
        model = Production_prosess

class Production_listforaddblockAdmin(admin.ModelAdmin):
    search_fields = ('productions',)
    list_display = ('productions', 'time', 'type', 'op','loc')
    # list_display = ('production_id', 'listforaddblock')

    class Meta:
        model = Production_listforaddblock

class DelblAdmin(admin.ModelAdmin):
    search_fields = ('productions',)
    list_display = ('productions', 'del_time', 'del_del', 'del_op')
    # list_display = ('production_id', 'listforaddblock')

    class Meta:
        model = Production_listfordelblock
admin.site.register(Production_prosess, ProcessAdmin)
admin.site.register(Production_listforaddblock,Production_listforaddblockAdmin)
admin.site.register(Production_listfordelblock,DelblAdmin)
