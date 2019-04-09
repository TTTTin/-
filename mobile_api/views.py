import json
from urllib.parse import urljoin

from avatar.models import Avatar
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render
from hashlib import md5

# Create your views here.
from rest_framework import permissions, status
from rest_framework.decorators import authentication_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from threadedcomments.models import ThreadedComment

from mobile_api.paginations import StandardResultsSetPagination, LargeResultsSetPagination
from mobile_api.serializers import MobileAPI_ProductionListSerializer, MobileAPI_ProductionDetailSerializer,PostCommentSerializer, \
    MobileAPI_FavoriteListSerializer, MobileAPI_UserInfoSerializer, CommentSerializer, MobileAPI_GalleryListSerializer
from scratch_api.models import Production, FavoriteProduction, BaseUser, User, LikeProduction, Gallery,galleryproduction


class MobileAPI_GalleryList(ListAPIView):
    """
    专题列表
    """
    model = Gallery
    serializer_class = MobileAPI_GalleryListSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        qs = Gallery.objects.filter(is_active=True)
        return qs


class MobileAPI_GalleryProductionList(ListAPIView):
    """
    获得一个专题的作品列表
    """

    model = Production
    serializer_class = MobileAPI_ProductionListSerializer
    permission_classes = (permissions.AllowAny,)

    # Support search and ordering
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name',)
    pagination_class = StandardResultsSetPagination
    ordering = ('-update_time',)

    def get_queryset(self):
        galleryId = self.kwargs['id']
        production_list = galleryproduction.objects.filter(admin_checked=True, gallery=galleryId).values('production')
        qs = Production.objects.filter(pk__in=production_list)
        type = self.request.query_params.get('type', None)
        if type:
            qs = qs.filter(tags__name__in=[type])
        return qs


class MobileAPI_ProductionList(ListAPIView):
    """
    作品列表
    """
    model = Production
    serializer_class = MobileAPI_ProductionListSerializer
    permission_classes = (permissions.AllowAny,)
    # Support search and ordering
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name',)
    pagination_class = StandardResultsSetPagination
    ordering = ('-update_time',)

    def get_queryset(self):
        qs = Production.objects.filter(is_active=True)
        type = self.request.query_params.get('type', None)
        if type:
            qs = qs.filter(tags__name__in=[type])
        return qs


class MobileAPI_ProductionDetail(RetrieveAPIView):
    """
    作品详情
    """
    model = Production
    serializer_class = MobileAPI_ProductionDetailSerializer
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        pk = self.kwargs['production']
        object = Production.objects.get(pk=pk)
        object.hit += 1
        # hit add 1 when access api
        object.save(update_fields=['hit'])
        return object

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MobileAPI_FavoriteList(ListAPIView):
    """
    收藏列表
    """
    model = Production
    serializer_class = MobileAPI_FavoriteListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    # Support search and ordering
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name',)
    pagination_class = LargeResultsSetPagination
    ordering = ('-update_time',)

    def get_queryset(self):
        user = self.request.user
        list = FavoriteProduction.objects.filter(user=user).values('production')
        return Production.objects.filter(pk__in=list, is_active=True)


class MobileAPI_UserInfo(RetrieveAPIView):
    """
    获得个人信息
    """
    model = User
    serializer_class = MobileAPI_UserInfoSerializer
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        return user

class MobileAPI_UserProductionList(ListAPIView):
    """
    获得一个用户的所有作品
    """
    model = Production
    serializer_class = MobileAPI_FavoriteListSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = LargeResultsSetPagination
    ordering = ('-update_time',)
    filter_backends = (OrderingFilter,)

    def get_queryset(self):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        return Production.objects.filter(is_active=True, author=user)


def mobileAPI_avatar(self, username):
    """
    获得用户的头像
    """
    response_data = {}
    try:
        user = BaseUser.objects.get(username=username)
        response_data['url'] = urljoin("http://www.tuopinpin.com/", Avatar.objects.get(user=user).get_absolute_url())
    except:
        pass
    return HttpResponse(json.dumps(response_data), content_type="application/json")


class MobileAPI_ProductionInfo(APIView):
    """
    API to get ProductionInfo
    """
    def judge_if_like(self, user, request, obj):
        user = user
        token = None
        if user.is_anonymous():
            # if a anonymous user, generate token according to IP and UA
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META['REMOTE_ADDR'])
            s = u"".join((ip_address, request.META.get('HTTP_USER_AGENT', '')))
            token = md5(s.encode('utf-8')).hexdigest()
            print(token)
            user = None
        return LikeProduction.objects.filter(user=user, token=token, production=obj).exists()

    def get(self, request, *args, **kwargs):
        obj = Production.objects.get(pk=self.kwargs['production'])
        response_data = {'favorite_count': FavoriteProduction.objects.filter(production=obj).count()}
        if not request.user.is_anonymous():
            response_data['if_favorite'] = FavoriteProduction.objects.filter(user=request.user, production=obj).exists()
        response_data['if_like'] = self.judge_if_like(self.request.user, request, obj)
        response_data['tags'] = obj.tags.names()
        # print(list(obj.tags.names()))
        return Response(response_data)


class MobileAPI_Comment(ListAPIView):
    """
    API to list comment recursively
    """
    model = ThreadedComment
    serializer_class = CommentSerializer

    def get_queryset(self):
        model_type = self.kwargs['type']
        pk = self.kwargs['pk']
        content_type = ContentType.objects.get(model=model_type)
        qs = ThreadedComment.objects.filter(content_type=content_type, object_pk=pk, parent=None).order_by(
            '-submit_date')
        return qs


class MobileAPI_PostComment(CreateAPIView):
    """
    API to post a comment
    """
    model = ThreadedComment
    serializer_class = PostCommentSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user
        data['content_type'] = ContentType.objects.get(model=data['content_type']).pk
        data['site'] = get_current_site(request).pk
        data['ip_address'] = request.META.get('HTTP_X_FORWARDED_FOR', request.META['REMOTE_ADDR'])
        serializer = PostCommentSerializer(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)
