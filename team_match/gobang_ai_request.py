
import datetime, re, json
from django.template.context_processors import csrf
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, render, redirect
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from course.models import Lesson
from scratch_api.models import User, Production
# from .models import JrProduction, JrLesson, JrTask
from .serializers import ProductionCreateSerializer, ProductionUpdateSerializer, ProductionForBattleCreateSerializer
import urllib.parse


from team_match.chessAI import naive_gobang_bot, smart_gobang_bot


@csrf_exempt
def naive_gobang_ai(request):
    chessboard, color = deserialize_chess_board(request.POST['chessboard']), request.POST['color']
    bot = naive_gobang_bot.GobangBot(chessboard, color)
    row, col = bot.action()
    row, col = row + 1, col + 1
    response = HttpResponse(json.dumps({'row': row, 'col': col}))
    return response


@csrf_exempt
def smart_gobang_ai(request):
    chessboard, color = deserialize_chess_board(request.POST['chessboard']), request.POST['color']
    bot = smart_gobang_bot.GobangBot(chessboard, int(color))
    score, row, col = bot.deep_go_gradually()
    row, col = row + 1, col + 1
    response = HttpResponse(json.dumps({'row': row, 'col': col}))
    return response


def deserialize_chess_board(serialized_chess_board):
    chess_board = []
    serialized_chess_board = serialized_chess_board.strip().split(';')
    for line in serialized_chess_board:
        chess_board.append([int(obj) for obj in line.split(',')])
    return chess_board

