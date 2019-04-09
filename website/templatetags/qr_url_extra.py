import datetime
from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from scratch_api.models import FavoriteProduction, Production, BaseUser, User

register = template.Library()


@register.assignment_tag(name='get_qr_url')
def get_qr_url(obj):
    return 'http://scratch.tuopinpin.com/mobile/index.html?' + obj.file.url