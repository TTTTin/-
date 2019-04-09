import datetime
from django import template

from scratch_api.models import FavoriteProduction, Teacher,User

register = template.Library()

@register.simple_tag(name='get_name', takes_context=True)
def get_name(context):
    user = context['request'].user
    print(user)
    try:
        return Teacher.objects.get(username=user).name
    except Exception as e:
        return user.username

@register.simple_tag(name='getuser_name', takes_context=True)
def getuser_name(context):
    user = context['request'].user
    print('username',user)
    try:
        return User.objects.get(username=user).name
    except Exception as e:
        return user.username