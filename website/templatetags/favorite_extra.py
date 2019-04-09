from django import template
from hashlib import md5
from scratch_api.models import FavoriteProduction, LikeProduction,FavoriteGallery,LikeGallery,galleryproduction

register = template.Library()


@register.simple_tag(name='count_production_favorite')
def count_production_favorite(obj):
    """
    :param obj: production object
    :return: count favorites of a production
    """
    return FavoriteProduction.objects.filter(production=obj).count()


@register.assignment_tag(name='get_if_favorite', takes_context=True)
def if_favorite(context, obj):
    """
    judge whether a user have favorite a production
    :param context: context of request
    :param obj: production
    :return: whether a user have favorite a production

    """
    user = context['request'].user
    if FavoriteProduction.objects.filter(user=user, production=obj).exists():
        return True
    else:
        return False


@register.assignment_tag(name='get_if_like', takes_context=True)
def if_like(context, obj):
    """
    judge if a user like a production
    :param context: context of a user
    :param obj: production object
    :return:
    """
    user = context['request'].user
    token = None
    if user.is_anonymous():
        # if a anonymous user, generate token according to IP and UA
        request = context['request']
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META['REMOTE_ADDR'])
        s = u"".join((ip_address, request.META.get('HTTP_USER_AGENT', '')))
        token = md5(s.encode('utf-8')).hexdigest()
        user = None
    if LikeProduction.objects.filter(user=user, token=token, production=obj).exists():
        return True
    else:
        return False




# 以下是gallery专题部分的点赞和收藏函数


@register.simple_tag(name='count_gallery_favorite')
def count_gallery_favorite(obj):
    """
    :param obj: production object
    :return: count favorites of a production
    """
    return FavoriteGallery.objects.filter(gallery=obj).count()


@register.assignment_tag(name='get_if_gallery_favorite', takes_context=True)
def if_gallery_favorite(context, obj):
    """
    judge whether a user have favorite a production
    :param context: context of request
    :param obj: production
    :return: whether a user have favorite a production

    """
    user = context['request'].user
    if FavoriteGallery.objects.filter(user=user, gallery=obj).exists():
        return True
    else:
        return False



@register.assignment_tag(name='get_if_gallery_like', takes_context=True)
def if_gallery_like(context, obj):
    """
    judge if a user like a production
    :param context: context of a user
    :param obj: production object
    :return:
    """
    user = context['request'].user
    token = None
    if user.is_anonymous():
        # if a anonymous user, generate token according to IP and UA
        request = context['request']
        s = u"".join((request.META['REMOTE_ADDR'], request.META.get('HTTP_USER_AGENT', '')))
        token = md5(s.encode('utf-8')).hexdigest()
        user = None
    if LikeGallery.objects.filter(user=user, token=token, gallery=obj).exists():
        return True
    else:
        return False

@register.assignment_tag(name='get_if_production_submit', takes_context=True)
def get_if_production_submit(context, obj):
    galleryObject = context['galleryObject']
    print(obj)

    if galleryproduction.objects.filter(gallery_id = galleryObject.id,production_id=obj).exists():
        return True
    else:
        return False

