from django.conf.urls import include, url

from qa.ajax_views import ajax_vote_question, ajax_vote_answer
from . import views

app_name = 'qa'


urlpatterns = [
    url(r'^$', views.QuestionIndexView.as_view(), name='qa_index'),

    url(r'^question/(?P<pk>\w+)/$',
        views.QuestionDetailView.as_view(), name='qa_detail'),

    url(r'^new-question/$', views.CreateQuestionView.as_view(), name='qa_create_question'),

    url(r'^edit-question/(?P<question_id>\d+)/$',
        views.UpdateQuestionView.as_view(),name='qa_update_question'),

    url(r'^answer/edit/(?P<answer_id>\d+)/$',
        views.UpdateAnswerView.as_view(), name='qa_update_answer'),

    url(r'^vote/question/(?P<question>\w+)/(?P<value>\w+)/$', ajax_vote_question,  name='vote_question'),

    url(r'^vote/answer/(?P<answer>\w+)/(?P<value>\w+)/$', ajax_vote_answer, name='vote_answer'),
]