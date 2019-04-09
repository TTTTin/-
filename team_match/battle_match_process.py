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
from team_match.battle_class import gobang_battle
from django.core.cache import cache


@csrf_exempt
def battle_match_request(request):
    ret = {}
    if cache.has_key(WEBSOCKET_COUNT_KEY) and cache.get(WEBSOCKET_COUNT_KEY) >= MAX_WEBSOCKET_COUNT:
        ret['start'] = False
        ret['msg'] = 'no websocket resource'
        return HttpResponse(json.dumps(ret))

    game_id = request.POST['game_id']
    matchGame = get_object_or_404(MatchGame, id=game_id)
    production_id_1 = matchGame.arrange.left.production.production.id
    production_id_2 = matchGame.arrange.right.production.production.id
    if matchGame.kind == 1:
        production_id_1, production_id_2 = production_id_2, production_id_1

    opCode = random_opcode()

    battle_obj = gobang_battle(opCode, production_id_1, production_id_2, '1')

    battle_obj.start()

    ret['start'] = True
    ret['opCode'] = opCode
    # 先手作品production_id_1， 后手作品production_id_2
    # ret['production_id_1'] = production_id_1
    # ret['production_id_2'] = production_id_2

    return HttpResponse(json.dumps(ret))


@csrf_exempt
def battle_match_start(request):
    ret = {}
    opCode = request.POST['opCode']
    if not cache.has_key(opCode):
        ret['start'] = False
        ret['msg'] = 'the battle list is full'
        return HttpResponse(json.dumps(ret))

    ret['start'] = True
    # 获取对战双方的作品id
    battle_obj = cache.get(opCode)
    production_id_1 = battle_obj.production_id_1
    production_id_2 = battle_obj.production_id_2
    #  启动对战双方的作品
    _thread.start_new_thread(run_scratch_production, (production_id_1, opCode, '1'))
    _thread.start_new_thread(run_scratch_production, (production_id_2, opCode, '2'))

    return HttpResponse(json.dumps(ret))



