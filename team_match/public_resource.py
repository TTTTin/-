import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random
from team_match.run_production import run_scratch_production

from django.core.cache import cache

MAX_WEBSOCKET_COUNT = 20
WEBSOCKET_COUNT_KEY = 'websocket_count_key'
CHARSET = '0123456789ABCDEFGHJKMNPQRSTVWXYZabcdefghijklmnpqrstuvwxyz'
LENGTH = 16

MAX_READY_SIGNAL_REPEATED = 6

def random_opcode():
    new_code = ""
    for i in range(LENGTH):
        new_code += CHARSET[random.randrange(0, len(CHARSET))]
    if cache.has_key(new_code):
        return random_opcode()
    return new_code

class BattleConsumer(WebsocketConsumer):
    def connect(self):
        # 当 websocket 一链接上以后触发该函数
        self.start = False
        self.ready_signal_count = 0
        self.opCode = self.scope['url_route']['kwargs']['opCode']
        print("random connect...")
        if cache.has_key(self.opCode):
            if not cache.has_key(WEBSOCKET_COUNT_KEY):
                cache.set(WEBSOCKET_COUNT_KEY, 1)
            else:
                cache.set(WEBSOCKET_COUNT_KEY, cache.get(WEBSOCKET_COUNT_KEY) + 1)
            print("websocket count : ", cache.get(WEBSOCKET_COUNT_KEY))
            self.room_group_name = 'battle_%s' % self.opCode
            # 把当前链接添加到对战室
            # 注意 `group_add` 只支持异步调用，所以这里需要使用`async_to_sync`转换为同步调用
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            # 接受该链接
            self.accept()


    def disconnect(self, close_code):
        # 断开链接是触发该函数
        # 将该链接移出聊天室
        print("random disconnect...")
        if cache.has_key(self.opCode):
            cache.set(WEBSOCKET_COUNT_KEY, cache.get(WEBSOCKET_COUNT_KEY) - 1)
            print("websocket count : ", cache.get(WEBSOCKET_COUNT_KEY))
            battle_obj = cache.get(self.opCode)
            battle_obj.remove_channel(self.channel_name)

            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )

    def receive(self, text_data):
        # 前端发送来消息时，通过这个接口传递
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # 发送消息到当前聊天室
        if message['type'] == 'readySignal':
            self.ready_signal_count += 1
            battle_obj = cache.get(self.opCode)
            if self.ready_signal_count == 1:
                role = message['role']
                battle_obj.add_channel(self.channel_name, 'player_' + role)
                if battle_obj.player_count() == battle_obj.PLAYER_NUM:
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'transform_datail',
                            'message': battle_obj.send_start()
                        }
                    )
            # 一方已经准备很久，另一方仍未准备，则比赛终止
            elif self.ready_signal_count > MAX_READY_SIGNAL_REPEATED:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'transform_datail',
                        'message': {'type': 'gameEnd'}
                    }
                )
        elif message['type'] == 'action':
            battle_obj = cache.get(self.opCode)
            over = battle_obj.action_and_judge_game_over(message)
            message['gameEnd'] = over
            if over:
                battle_obj.end()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'transform_datail',
                    'message' : message
                }
            )

    # 从聊天室拿到消息，后直接将消息返回回去
    def transform_datail(self, event):
        message = event['message']
        print(message)
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

