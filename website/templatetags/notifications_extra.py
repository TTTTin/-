from django import template

from scratch_api.models import FavoriteProduction

# register = template.Library()
# @register.simple_tag(name='count_production_favorite', takes_context=True)
# def count_production_favorite(context):
#     user = context['request'].user
#     user.
#     return FavoriteProduction.objects.filter(production=obj).count()