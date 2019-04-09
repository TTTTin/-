from team_match.models import MatchGame, GameDetail
import _thread
from django.shortcuts import render, HttpResponse, get_object_or_404
import json, collections
from team_match.battle_judge import gobang_judge
from collections import deque
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random
from team_match.run_production import run_scratch_production
from team_match.public_resource import random_opcode, MAX_WEBSOCKET_COUNT, WEBSOCKET_COUNT_KEY
from team_match.battle_class import gobang_battle, snake_battle
from django.core.cache import cache

@csrf_exempt
def battle_with_others_request(request):
    ret = {}
    if cache.has_key(WEBSOCKET_COUNT_KEY) and cache.get(WEBSOCKET_COUNT_KEY) >= MAX_WEBSOCKET_COUNT:
        ret['start'] = False
        ret['msg'] = 'no websocket resource'
        return HttpResponse(json.dumps(ret))

    opCode = random_opcode()
    # 发起挑战的作品id
    production_id_1 = request.POST['productionID1']
    # 接受挑战的作品id
    production_id_2 = request.POST['productionID2']
    # 1 发起挑战的作品先走， 2  接受挑战的作品先走
    first_go = request.POST['firstGo']

    mess = '2' if first_go == '1' else '1'

    _thread.start_new_thread(run_scratch_production, (production_id_2, opCode, mess))

    if request.POST['gameType'] == '1':
        battle_obj = gobang_battle(opCode, production_id_1, production_id_2, first_go)
    else:
        battle_obj = snake_battle(opCode, production_id_1, production_id_2, first_go)

    # battle_obj = gobang_battle(opCode, production_id_1, production_id_2, first_go)

    battle_obj.start()

    # 标志游戏是否 可以开始
    # 为true表示此game未在battle_list中，两玩家的作品未在map_production_to_battle中 比赛可以开始
    ret['start'] = True
    ret['opCode'] = opCode

    return HttpResponse(json.dumps(ret))


