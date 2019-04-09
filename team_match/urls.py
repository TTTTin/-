from django.conf.urls import include, url
from team_match.views import CompetitionWebsiteList, CompetitionDetail, QuestionDetail, MatchGameDetail,show_gobang_battle, ProductionTemplate, ProductionList
from team_match.upload_download_delete import UploadProduction, DownloadProduction, DeleteProduction
from team_match.battle_with_ai_process import battle_with_ai_request
from team_match.battle_with_others_process import battle_with_others_request
from django.views.static import serve
from team_match.battle_match_process import battle_match_request, battle_match_start

from team_match import gobang_ai_request

app_name = 'team_match'

urlpatterns = [
    url(r'^$', CompetitionWebsiteList.as_view(), name='team_match_index'),
    url(r'^competition(?P<competition_id>[0-9]+)/$', CompetitionDetail.as_view(), name="team_match_competitionDetail"),
    url(r'^question(?P<question_id>[0-9]+)/$', QuestionDetail.as_view(), name="team_match_questionDetail"),
    url(r'^replay_game(?P<game_id>[0-9]+)/$', MatchGameDetail.as_view(), name="team_match_gameDetail"),

    url(r'^production/(?P<who>[a-z]+)/$', ProductionList.as_view(), name="team_match_production"),

    url(r'^create_production/$', ProductionList.as_view(), name="team_match_create_production"),

    url(r'^production/scratch/(?P<path>.*)', serve, {'document_root' : 'team_match/templates/'}),

    url(r'^show_gobang_battle/$',show_gobang_battle),

    url(r'^production_template/$', ProductionTemplate.as_view()),

    url(r'^load_production/$', DownloadProduction.as_view()),

    url(r'^upload_production/$', UploadProduction.as_view()),

    url(r'^delete_production/$', DeleteProduction.as_view(), name='team_match_delete_production'),

    url(r'^battle_with_ai/$', battle_with_ai_request, name="team_match_battle_with_ai"),

    url(r'^battle_with_others/$', battle_with_others_request, name="team_match_battle_with_others"),

    url(r'^battle_match_request/$', battle_match_request, name="team_match_battle_match_request"),

    url(r'^battle_match_start/$', battle_match_start, name="team_match_battle_match_start"),

    url(r'^naive_gobang_ai_request/$', gobang_ai_request.naive_gobang_ai),

    url(r'^smart_gobang_ai_request/$', gobang_ai_request.smart_gobang_ai)

]

