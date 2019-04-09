from django.conf.urls import include, url

from . import views

app_name = 'mobile_api'

urlpatterns = [

    url(r'^production_list/$', views.MobileAPI_ProductionList.as_view(), name='mobile_api_production_list', ),
    url(r'^production_detail/(?P<production>.+)/$', views.MobileAPI_ProductionDetail.as_view(),
        name='mobile_api_production_list'),
    url(r'^favorite_list/$', views.MobileAPI_FavoriteList.as_view(), name='mobile_api_production_list'),
    url(r'^avatar/(?P<username>.+)/$', views.mobileAPI_avatar, name='mobile_avatar'),
    url(r'^user_production_list/(?P<username>.+)/$', views.MobileAPI_UserProductionList.as_view()),
    url(r'^user_info/(?P<username>.+)/$', views.MobileAPI_UserInfo.as_view()),
    url(r'^production_info/(?P<production>.+)/$', views.MobileAPI_ProductionInfo.as_view()),
    url(r'^comment/(?P<type>.+)/(?P<pk>.+)$', views.MobileAPI_Comment.as_view()),
    url(r'^post_comment/$', views.MobileAPI_PostComment.as_view()),
    url(r'^gallery_list/$', views.MobileAPI_GalleryList.as_view(), name='mobile_api_gallery_list'),
    url(r'^gallery_production_list/(?P<id>.+)/$', views.MobileAPI_GalleryProductionList.as_view(), name='mobile_api_galleryproductionlist'),
]
