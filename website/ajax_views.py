import json
from django.http import HttpResponse
from hashlib import md5
from scratch_api.models import FavoriteProduction, User, Production,Gallery, LikeProduction, CommentEachOther,FavoriteGallery,LikeGallery


def website_ajax_favorite(request, production):
    """
    ajax favorite a production
    :param request:
    :param production: production object
    :return: a json of result
    """
    c = {}
    baseuser = request.user
    user = User.objects.get(username=baseuser)
    if FavoriteProduction.objects.filter(user=user, production=production).exists():
        # if have favorite, delete it
        FavoriteProduction.objects.get(user=user, production=production).delete()
    else:
        FavoriteProduction(user=user, production_id=production).save()
    response_data = {}
    response_data['result'] = 'Success!'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def website_ajax_like(request, production):
    """
    similar to website_ajax_favorite
    :param request:
    :param production:
    :return:
    """
    production = Production.objects.get(pk=production)
    user = request.user
    response_data = {}
    try:
        if user.is_anonymous():
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META['REMOTE_ADDR'])
            s = u"".join((ip_address, request.META.get('HTTP_USER_AGENT', '')))
            token = md5(s.encode('utf-8')).hexdigest()
            if not LikeProduction.objects.filter(user=None, token=token, production=production).exists():
                LikeProduction(user=None, token=token, production=production).save()
                production.like += 1
                production.save(update_fields=('like',))
        else:
            if not LikeProduction.objects.filter(user=user, token=None, production=production):
                LikeProduction(user=user, token=None, production=production).save()
                production.like += 1
                production.save(update_fields=('like',))
        response_data['result'] = 'Success!'

    except Exception as e:
        print(e)
        response_data['result'] = 'Fail!'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def website_ajax_comment_eachother(request, production):
    """
    :param request:
    :param production: production object
    :return: a json of result
    """
    c = {}
    response_data = {}
    baseuser = request.user
    score = int(request.GET.get("score"))
    try:
        user = User.objects.get(username=baseuser)
        if CommentEachOther.objects.filter(user=user, production=production).exists():
            #减去之前的评分 加上新的评分
            project = Production.objects.get(pk=production)
            project.comment_eachother_all_score = project.comment_eachother_all_score - CommentEachOther.objects.get(user=user, production=production).comment_score
            project.comment_eachother_all_score = project.comment_eachother_all_score + score
            project.save(update_fields=("comment_eachother_all_score", ))

            p = CommentEachOther.objects.get(user=user, production=production)
            p.comment_score = score
            p.save()
        else:
            #直接加上新的评分
            project = Production.objects.get(pk=production)
            CommentEachOther.objects.create(user=user, production=project, comment_score=score)

            project.comment_eachother_all_score = project.comment_eachother_all_score + score
            project.save(update_fields=("comment_eachother_all_score", ))
        response_data['result'] = 'Success!'
    except Exception as e:
        print(e)
        response_data['result'] = 'Fail!'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def website_inbox_readall(request):
    """
    mark readall in inbox
    :param request:
    :return:
    """
    c = {}
    user = request.user
    user.notifications.mark_all_as_read()
    response_data = {}
    response_data['result'] = 'Success!'
    return HttpResponse(json.dumps(response_data), content_type="application/json")




def website_ajax_gallery_favorite(request, gallery):
    """
    ajax favorite a gallery
    :param request:
    :param production: gallery object
    :return: a json of result
    """
    c = {}
    baseuser = request.user
    user = User.objects.get(username=baseuser)
    if FavoriteGallery.objects.filter(user=user, gallery=gallery).exists():
        # if have favorite, delete it
        FavoriteGallery.objects.get(user=user, gallery=gallery).delete()
    else:
        FavoriteGallery(user=user, gallery_id=gallery).save()
    response_data = {}
    response_data['result'] = 'Success!'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def website_ajax_gallery_like(request, gallery):
    """
    similar to website_ajax_gallery_favorite
    :param request:
    :param production:gallery object
    :return:
    """
    gallery = Gallery.objects.get(pk=gallery)
    user = request.user
    response_data = {}
    try:
        if user.is_anonymous():
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META['REMOTE_ADDR'])
            s = u"".join((ip_address, request.META.get('HTTP_USER_AGENT', '')))
            token = md5(s.encode('utf-8')).hexdigest()
            print(token)
            if not LikeGallery.objects.filter(user=None, token=token, gallery=gallery).exists():
                LikeGallery(user=None, token=token, gallery=gallery).save()
                gallery.like += 1
                gallery.save(update_fields=('like',))
        else:
            if not LikeGallery.objects.filter(user=user, token=None, gallery=gallery):
                LikeGallery(user=user, token=None, gallery=gallery).save()
                gallery.like += 1
                gallery.save(update_fields=('like',))
        response_data['result'] = 'Success!'

    except Exception as e:
        print(e)
        response_data['result'] = 'Fail!'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def update_ajax_liveTimeSum(request,productionid,liveTimeSum):
    """
    ajax update the liveTimeSum
    :param request:
    :param time: liveTimeSum,liveTimeSum
    :return: a json of result
    """

    print("productionid="+productionid)
    response_data = {}
    production = Production.objects.get(pk=productionid)
    user = User.objects.get(pk = production.author_id)
    production.production_duration += int(liveTimeSum)    #记录的时间单位是毫秒
    production.save(update_fields=('production_duration',))
    print("production.production_duration增加了：" + str(liveTimeSum))
    print("production.production_duration=" + str(production.production_duration))
    user.coding_duration +=int(liveTimeSum)
    user.save(update_fields=('coding_duration',))
    print("user.coding_duration=" + str(user.coding_duration))
    response_data['result'] = 'Success!'
    return HttpResponse(json.dumps(response_data), content_type="application/json")