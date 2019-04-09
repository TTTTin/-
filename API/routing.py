from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from django.conf.urls import url

import team_match.public_resource
import team_match.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    # 普通的HTTP请求不需要我们手动在这里添加，框架会自动加载过来
    'websocket': AuthMiddlewareStack(
        URLRouter(
            team_match.routing.websocket_urlpatterns
            # [url('ws/chatroom/<str:room_name>/', chat.consumers.ChatConsumer),]
        ),
    ),
    "channel" : ChannelNameRouter({
        "service-detection": team_match.public_resource.BattleConsumer,
    })
})