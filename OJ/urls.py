from django.conf.urls import include, url

from OJ.admin import oj_admin_site
from OJ.ajax_views import SubmissionView, CheckView, ProblemSubmissionHistoryListView
from OJ.views import Website_ProblemList, ProblemDetail, SubmissionDetail, PersonalDetail
from OJ.teacher_views import GetProblem, ProblemCreate, ProblemList, ProblemUpdate, ProblemDelete,GetTestCases,TestCasesList,test_cases_create, test_cases_update, test_cases_delete


app_name = 'OJ'

urlpatterns = [
    url(r'^problems/$', Website_ProblemList.as_view(), name='problem_list'),
    url(r'^problem/(?P<pk>.+)/$', ProblemDetail.as_view(), name='problem_detail'),
    url(r'^submission/(?P<pk>.+)/$', SubmissionDetail.as_view(), name='submission_detail'),
    url(r'^personal/(?P<username>.*)/$', PersonalDetail.as_view(), name='oj_personal_detail'),

    # url(r'^/get_problem/$', GetProblem.as_view()),
    # url(r'^problem_management/$', ProblemList.as_view()),

      url(r'^get_problem/$', GetProblem.as_view()),
      url(r'^problem_management/$', ProblemList.as_view()),
      url(r'^problem_management/new/$',ProblemCreate.as_view()),
      url(r'^problem_management/(?P<problem>\w+)/$', ProblemUpdate.as_view()),
      url(r'^problem_management/(?P<problem>\w+)/delete/$', ProblemDelete.as_view()),

      url(r'^get_test_cases/(?P<problem>\w+)/$', GetTestCases.as_view()),
      url(r'^test_cases_management/(?P<problem>\w+)/$', TestCasesList.as_view()),
      url(r'^test_cases_management/(?P<problem>\w+)/new/$', test_cases_create),
      url(r'^test_cases_management/(?P<problem>\w+)/(?P<test_cases>\w+)/$', test_cases_update),
      url(r'^test_cases_management/(?P<problem>\w+)/(?P<test_cases>\w+)/delete/$', test_cases_delete),

    # url(r'^t/get_problem/$', GetProblem.as_view()),
    # url(r'^t/problem_management/$', ProblemList.as_view()),
    # url(r'^t/problem_management/new/$', ProblemCreate.as_view()),
    # url(r'^t/problem_management/(?P<problem>\w+)/$', ProblemUpdate.as_view()),
    # url(r'^t/problem_management/(?P<problem>\w+)/delete/$', ProblemDelete.as_view()),

    # url(r'^t/get_test_cases/(?P<problem>\w+)/$', GetTestCases.as_view()),
    # url(r'^t/test_cases_management/(?P<problem>\w+)/$', TestCasesList.as_view()),
    # url(r'^t/test_cases_management/(?P<problem>\w+)/new/$', TestCasesCreate.as_view()),
    # url(r'^t/test_cases_management/(?P<problem>\w+)/(?P<test_cases>\w+)/$', TestCasesUpdate.as_view()),
    # url(r'^t/test_cases_management/(?P<problem>\w+)/(?P<test_cases>\w+)/delete/$', TestCasesDelete.as_view()),


]

urlpatterns += [
    url(r'^submit/$', SubmissionView.as_view(), name='submission'),
    url(r'^check/$', CheckView.as_view(), name='check'),
    url(r'^problem_submission_history/$', ProblemSubmissionHistoryListView.as_view(),
        name='problem_submission_history'),
]

urlpatterns += [
    url(r'^admin/', oj_admin_site.urls),
]