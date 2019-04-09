import datetime
from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from qa.models import Answer, Question
from scratch_api.models import FavoriteProduction, Production, BaseUser, User, FormatClass, FormatSchool

register = template.Library()


@register.assignment_tag(name='get_obj_url')
def get_obj_url(obj):
    """
    if notifications have object, return the objects's detail url
    for example, if obj is a production object, return production url
    :param obj:
    :return:
    """
    if type(obj) == Production:
        # print(obj.pk)
        return '/productdetail/' + str(obj.pk)
    elif type(obj) == Answer:
        return reverse('qa:qa_detail', kwargs={'pk':obj.question.pk})+'#answer'+str(obj.pk)
    elif type(obj) == Question:
        return reverse('qa:qa_detail', kwargs={'pk':obj.pk})
    elif type(obj) == FormatClass:
        return '/t/apply_management/'
    elif type(obj) == FormatSchool:
        return '/t/apply_management/'
    else:
        return None