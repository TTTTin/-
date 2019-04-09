import datetime
from django import template

from scratch_api.models import FavoriteProduction, Teacher,User,Competition,CompetitionUser,CompetitionQuestion
import time
import datetime
from django.utils.timezone import utc
from django.utils.timezone import localtime
register = template.Library()


@register.simple_tag(name='get_competition_attend', takes_context=True)
def competition_attend(context, competition):
    """
    :param obj: production object
    :return: count favorites of a production
    """
    user = context['request'].user
    c = competition
    has_authority = False
    can_attend = False
    if not user.is_anonymous():
        p = competition.user.all().filter(username=user)
        competitionuser = CompetitionUser.objects.filter(competition =c,user = user)
        if p.exists() and competitionuser:
            has_authority = True
            delay_time = competitionuser.first().delay_time
            if int(time.mktime(time.localtime(time.time())))>(int(time.mktime(c.start_time.timetuple()))+8*3600) and int(time.mktime(time.localtime(time.time()))) < (int(time.mktime(c.stop_time.timetuple())+8*3600)+delay_time*60):
                can_attend = True
                return {"has_authority": has_authority, "can_attend": can_attend}
    return {"has_authority": has_authority, "can_attend": can_attend}

# @register.simple_tag(name="get_competition_attend_authority", takes_context=True)
# def competition_attend_authority(context, competition):
#     """
#     :param context:
#     :param competition:
#     :return: have authority return True
#     """
#     user = context["request"].user
#     c = competition
#     if (not user.is_anonymous()) and user.is_authenticated():
#         competitionuser

@register.simple_tag(name='get_productionname', takes_context=True)
def get_name(context, question):
    user = context['request'].user
    productionlist = None
    if question.production.all().filter(author=user):
        productionlist = question.production.all().get(author=user)
    return productionlist
