# from django.urls import ur
from django.conf.urls import url

from .public_resource import BattleConsumer


websocket_urlpatterns = [ # 路由，指定 websocket 链接对应的 consumer
    # url('ws/chatroom/<str:room_name>/', consumers.ChatConsumer),
    url(r'^ws/battleroom/(?P<opCode>[^/]+)/$', BattleConsumer),
]