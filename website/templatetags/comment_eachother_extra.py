from django import template
from scratch_api.models import CommentEachOther, TeacherScore

register = template.Library()


@register.simple_tag(name='count_production_score', takes_context=True)
def count_production_score(context, obj):
    user = context['request'].user
    if CommentEachOther.objects.filter(user=user, production=obj).exists():
        #print(CommentEachOther.objects.get(user=user, production=obj).comment_score)
        return CommentEachOther.objects.get(user=user, production=obj).comment_score
    else:
        return 0


@register.simple_tag(name='get_teacher_score_of_production_by_id', takes_context=True)
def get_teacher_score_of_production_by_id(context, obj):
    teacher_score = TeacherScore.objects.filter(production_id=obj)
    if teacher_score.exists():
        return teacher_score.first().score
    else:
        return "暂时还没有评分"


@register.simple_tag(name='get_teacher_comment_of_production_by_id', takes_context=True)
def get_teacher_comment_of_production_by_id(context, obj):
    teacher_score = TeacherScore.objects.filter(production_id=obj)
    if teacher_score.exists():
        return teacher_score.first().comment
    else:
        return "暂时还没有评价"



# @register.assignment_tag(name='get_if_favorite', takes_context=True)
# def if_favorite(context, obj):
#     """
#     judge whether a user have favorite a production
#     :param context: context of request
#     :param obj: production
#     :return: whether a user have favorite a production
#
#     """
#     user = context['request'].user
#     if FavoriteProduction.objects.filter(user=user, production=obj).exists():
#         return True
#     else:
#         return False

