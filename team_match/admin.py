from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.MatchProduction)
admin.site.register(models.MatchArrange)
admin.site.register(models.MatchGame)
admin.site.register(models.GameDetail)
admin.site.register(models.ProductionForBattle)

# class MatchProductionAdmin(admin.ModelAdmin):
#     list_display = ("pk", "production", "group","com_question", "score", )
#     search_fields = ("production__id", "production__name", "group", "com_question")
#
#
# class MatchArrangeAdmin(admin.ModelAdmin):
#     list_display = ("pk", "left", "right", "type", "result")
#     search_fields = ("pk",
#                      "left__production__id",
#                      "left__production__name",
#                      "right__production__id",
#                      "right__production__name",
#                      "type",
#                      )
#
#
# class MatchGameAdmin(admin.ModelAdmin):
#     list_display = ("pk", "arrange", "game", "kind", "code", )
#     search_fields = ("pk",
#                      "arrange__left__production__id",
#                      "arrange__left__production__name",
#                      "arrange__right__production__id",
#                      "arrange__right__production__name",
#                      "game",
#                      "code",
#                      )
#
#
# class GameDetailAdmin(admin.ModelAdmin):
#     list_display = ("pk", "match_game", "operator", "round", )
#     search_fields = ("pk", "match_game__pk")