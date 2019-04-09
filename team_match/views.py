
from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from django.views.generic import DetailView, View
from django_filters.views import FilterView
from django_tables2 import SingleTableView, SingleTableMixin
from django.views import View
from rest_framework.generics import ListAPIView
from django.views.generic import ListView
from scratch_api.models import User, Production, Competition, CompetitionQuestion
from .models import MatchArrange, MatchProduction, GameDetail, MatchGame, ProductionForBattle
from django.views.decorators.csrf import csrf_exempt
import json
from django.core import serializers



class CompetitionWebsiteList(ListView):
    template_name = "team_match_index.html"
    context_object_name = "competitions"
    model = Competition

    def get_queryset(self):
        return Competition.objects.all()


class CompetitionDetail(ListView):
    model = CompetitionQuestion
    template_name = 'team_match_competitionDetail.html'
    context_object_name = "competitionQuestions"

    def get_queryset(self):
        com = get_object_or_404(Competition, id=self.kwargs.get('competition_id'))
        return super(CompetitionDetail, self).get_queryset().filter(competition=com)


class QuestionDetail(ListView):
    model = MatchArrange
    template_name = 'team_match_matchArrange.html'
    context_object_name = 'matchArrange'

    def get_queryset(self):
        questionObject = get_object_or_404(CompetitionQuestion, id=self.kwargs.get('question_id'))
        matchProductions = MatchProduction.objects.all().filter(com_question=questionObject)
        matchArranges = MatchArrange.objects.all()
        matchArrange = []
        for match in matchArranges:
            if match.left in matchProductions or match.right in matchProductions:
                matchArrange.append(match)
                # print(match)
        return matchArrange



class MatchGameDetail(ListView):
    model = GameDetail
    template_name = 'game_replay_by_jsonfile.html'
    context_object_name = 'gameDetail'

    def get_queryset(self):
        # game = get_object_or_404(MatchGame, id=self.kwargs.get('game_id'))
        # details = GameDetail.objects.all().filter(match_game=game).order_by('round')
        # gameDetail = []
        # for i in range(len(details)):
        #     c = {}
        #     c['operator'] = details[i].operator.__str__()
        #     c['detail'] = details[i].detail
        #     gameDetail.append(c)
        # # return json.dumps(gameDetail)
        # return gameDetail
        file_obj = open('team_match/resultfile.json')
        context = file_obj.read()
        detail_obj = json.loads(context)
        # print(detail_obj)
        return detail_obj['details']

class ProductionList(View):

    def get(self, request, who):
        if who == 'self':
            user_name = request.user
            production_list = ProductionForBattle.objects.all().filter(production__author__name=user_name)
            return render(request, 'self_production_list.html', {'production_list': production_list})
        elif who == 'others' or True:
            user_name = request.user
            production_list = ProductionForBattle.objects.all().exclude(production__author__name=user_name).order_by('kind_of_battle')
            return render(request, 'others_production_list.html', {'production_list' : production_list})

    @csrf_exempt
    def post(self, request, who):
        ret = {}
        user_name = request.user
        kind_of_battle = request.POST['kind_of_battle']
        if kind_of_battle == None:
            production_list = ProductionForBattle.objects.all().filter(production__author__name=user_name)
        else:
            kind_of_battle = int(kind_of_battle)
            production_list = ProductionForBattle.objects.all().filter(production__author__name=user_name, kind_of_battle=kind_of_battle)
        production_list = [[production.production.name, str(production.production.id)] for production in production_list]
        return HttpResponse(json.dumps({'production_list' : production_list}))


def show_gobang_battle(request):
    return render(request, 'team_match_show_gobang_battle.html')


class ProductionTemplate(ListAPIView):

    def post(self, request):
        if request.data['type'] == 'gobang':
            file = open('team_match/templates/template-gobang.sb3','rb')
            response = HttpResponse(file)
        elif request.data['type'] == 'snake':
            file = open('team_match/templates/template-snake.sb3', 'rb')
            response = HttpResponse(file)
        else:
            response = HttpResponse()
        return response



def create_production(request):
    if request.user.is_authenticated():
        return render(request, 'build/index.html')
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

