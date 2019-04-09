# -*- coding: utf-8 -*-
"""API URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from __future__ import absolute_import



from ckeditor_uploader.views import browse as ckeditor_browse
from ckeditor_uploader.views import upload as ckeditor_upload

from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView, password_reset
from django.views.decorators.cache import never_cache, cache_page
from django.views.generic import TemplateView, RedirectView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.authtoken import views

import qa
import scratch_api
from course.views import get_lesson, get_chapter, LessonView, TOCView, ChapterView, get_side_course, insert_behavior, \
    LessonListView
from scratch_api.models import User, Production
from scratch_api.serializers import UserSerializer, ProductionCreateSerializer
from scratch_api.views import CreateUserView, MyObtainAuthToken, FileDeleteView, FileListView, \
    FileCreateOrUpdateView, scratch, SchoolView, ClassListView, ClassCreateView, analysis, GetUserSchoolView, \
    ChangePasswordView, get_classes, get_homework_project, ProductionInfoUpdate, get_classmate_project_in_same_lesson, \
    ObtainAuthTokenByName, truename_class, truename_school, CompetitionWebsiteList, CompetitionWebsiteDetail, \
    CompetitionWebsiteSubmit, CompetitionWebsiteSubmitResult, getCompetitionQs, ExamListView, CompetitionQuestionUpdate, \
    AntiCheatingView, ExamFileCreateOrUpdateView, CompetionIsOver, GetProductionDes, GetServerTime, GetProductionId, \
    FormatSchoolView, get_format_classes, truename_format_school, truename_format_class, ObtainAuthTokenByTrueName

from scratch_api.teacher_views import download, grade, import_student,import_teacher, import_competition_user, GetCourse, GetChapter, CourseList, \
    CourseCreate, ChapterList,CompetitionCreate ,CompetitionListAdmin,CompProducAdminList,CompetitionUpdate,CompetitionDelete,\
    ChapterCreate, ChapterUpdate, CourseUpdate, CourseDelete, ChapterDelete,  \
    ChapterCreate, ChapterUpdate, CourseUpdate, CourseDelete, ChapterDelete, \
    StudentManagementResetPassword, MyPasswordChangeView,StudentAddUpdate,CompetitionUserList,GetCompetitionUser,\
    get_teachers_score_and_comment_of_productions_by_ids, StudentPasswordChangeView,StudentDelte,UpdateClassName,resetpwd,\
    get_teachers_score_and_comment_of_productions_by_ids, StudentPasswordChangeView,StudentDelte,UpdateClassName,resetpwd,competition_sign,production_rater,CompetitionListAdviser,\
    CompProAdviserList,GetComPro,CompProgressList,GetCompProducAdmin,CompProScoreFinal,GetCompProduc,GetProgressList,CompetitionUserUpdate
from scratch_api.teacher_views import download, grade, import_student, GetCourse, GetChapter, CourseList, \
    CourseCreate, ChapterList, \
    ChapterCreate, ChapterUpdate, CourseUpdate, CourseDelete, ChapterDelete, \
    ChapterCreate, ChapterUpdate, CourseUpdate, CourseDelete, ChapterDelete,\
    StudentManagementResetPassword, MyPasswordChangeView,StudentList, GetListStudent, updateschool, updateclass, \
    get_teachers_score_and_comment_of_productions_by_ids, StudentPasswordChangeView, StudentDelte, AllStudentDelte, GetTeacherTable, GetTeacher, TeacherSetting,Personalsetting,\
    AllPermissions, ChangeTeacherPermission, AddTeacherPermission, AddPositions, CheckPositions, CheckOnePositions, \
    CompetitionList,CompProducList,TeacherManagement

# from django.contrib.auth.views import auth_login
from django.contrib.auth import views as auth_views
from scratch_api.teacher_views import MyLoginView, index, ajax_school, ajax_class, ajax_student, \
    ajax_production, sidebar, signup
from website.ajax_views import website_ajax_favorite, website_inbox_readall, website_ajax_like, \
    website_ajax_comment_eachother,website_ajax_gallery_favorite,website_ajax_gallery_like,update_ajax_liveTimeSum
from website.ajax_bigdata_views import get_json_online_test
from website.views import WebsiteProductionList, website_productiondetail, website_login, website_logout, \
    website_inbox, \
    InboxUnreadList, InboxDeatil, InboxAllList, MyFavoriteList, remix_tree, ProductionRemixList, \
    UserSetting, StudentAddClass, WebsiteGalleryList, WebsiteGalleryDetail, website_submitProductiontToGallery, \
    submit_result, BigDataLocalJson, BigDataOnlineJson, WebsiteDownloadList, DataVisualizationList, DataVisualization, \
    dataVisualization_competition, dataVisualization_judge, \
    dataVisualization_student, dataVisualization_production, \
    fucking_idots, GalleryCreate, WebsiteUserPage, WebsiteMyClass, MyFormatClass, MoreProductionListView
import notifications.urls
from scratch_api.teacher_views import OrderList

from password_reset.views import recover
from password_reset import urls
from scratch_api.new_teacher_views import import_school, import_school_all, import_user, import_user_school, \
    import_user_class, import_user_class_nadmin, class_add_stu, \
    new_import_teacher, import_class, import_class_teacher, format_class_management, ClassManagementList, \
    StudentManagementList, \
    StudentManagementUpdate, GetStudent, ClassDelete, import_school_class, GetClass, get_all_school, get_all_class, \
    GetAllStudent, ClassManagementAdd, GetAddStudent, \
    GetStudentSou, AllStudentManagementUpdate, TeacherChangePasswordView, blank, \
    GetAllStudent, \
    GetStudentSou, AllStudentManagementUpdate, TeacherChangePasswordView, blank, aboutCT, CTei, aboutUs, \
    downloadScratch, downloadResource, apply_management, apply_submit

#from OJ.teacher_views import GetProblem, ProblemCreate, ProblemList


urlpatterns = [
    # 以下url是REST API的url
    url(r'^getservertime/$', GetServerTime),
    url(r'^getproductionid/$', GetProductionId),
    url(r'^scratch/$', TemplateView.as_view(template_name='scratch.html')),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/webshell/', include('webshell.urls')),
    url(r'^register', CreateUserView.as_view()),
    url(r'^login/', MyObtainAuthToken.as_view()),
    url(r'^loginName/', ObtainAuthTokenByName.as_view()),
    url(r'^loginTrueName/$', ObtainAuthTokenByTrueName.as_view()),
    url(r'^delete/', FileDeleteView.as_view()),
    url(r'^getUserSchool/', GetUserSchoolView.as_view()),
    url(r'^upload/', FileCreateOrUpdateView.as_view()),
    url(r'^examupload/', ExamFileCreateOrUpdateView.as_view()),
    url(r'^updateProductionInfo/', ProductionInfoUpdate.as_view()),
    url(r'^updateExamInfo/', CompetitionQuestionUpdate.as_view()),
    url(r'^getList/', FileListView.as_view()),
    url(r'^getexamList/', ExamListView.as_view()),
    url(r'^getproductiondes/',GetProductionDes.as_view()),
    url(r'^getqs/', getCompetitionQs),
    url(r'^getClassList/', ClassListView.as_view()),
    url(r'^createClass/', ClassCreateView.as_view()),

    url(r'^changePassword/', ChangePasswordView.as_view()),
    url(r'^teachersetting/(?P<pk>.+)/$', TeacherSetting.as_view(), name="teachersetting"),
    url(r'^t/personalsetting/', MyPasswordChangeView.as_view()),
    url(r'^t/change_password/$', TeacherChangePasswordView.as_view()),
	url(r'^accounts/password/change/', MyPasswordChangeView.as_view()),
    url(r'^accounts/password/$', PasswordChangeDoneView.as_view()),

    url(r'^analysis/', analysis),
    url(r'^school/', SchoolView.as_view()),
    url(r'^format_school/$', FormatSchoolView.as_view()),
    url(r'^crossdomain.xml', TemplateView.as_view(template_name='crossdomain.xml')),
]

urlpatterns += [
    # 以下url是教师端的url
    url(r'^t/$', MyLoginView.as_view(), name='login'),
    url(r'^t/index/$', index, name='index'),
    url(r'^t/signup/$',signup ,name='singup'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^t/download/', download, name='download'),
    url(r'^t/grade/', grade, name ='grade'),
    url(r'^t/production/(.+)/$', scratch_api.teacher_views.production, name='production'),
    url(r'^t/list/', scratch_api.teacher_views.list, name='list'),
    url(r'^t/test/', scratch_api.teacher_views.test, name="test"),
    url(r'^ajax/get_school$', ajax_school),
    url(r'^ajax/get_class$', ajax_class),
    url(r'^ajax/get_student$', ajax_student),
    url(r'^ajax/get_production$', ajax_production),
    url(r'^t/order/', OrderList.as_view(), name='order'),

    url(r'^sidebar/$', sidebar),
    url(r'^t/aboutus/$', aboutUs),
    url(r'^t/aboutct/$', aboutCT),
    url(r'^t/ctei/$', CTei),
    url(r'^t/blank/$', blank),
    url(r'^t/download_scratch/$', downloadScratch),
    url(r'^t/download_resource/$', downloadResource),
    # 可视化


    url(r'^t/dataVisualizationList/$',  DataVisualizationList.as_view(template_name='dataVisualizationList.html')),
    url(r'^t/dataVisualization/(?P<id>.+)$', DataVisualization,name='dataVisualization.html'),
    # url(r'^t/dataVisualization_agent/$',TemplateView.as_view(template_name='dataVisualization_agent.html')),
    #可视化分页面
    url(r'^t/dataVisualization_competition/(?P<id>.+)$', dataVisualization_competition,name='dataVisualization_competition.html'),
    url(r'^t/dataVisualization_student/(?P<id>.+)$', dataVisualization_student,name='dataVisualization_student.html'),
    url(r'^t/dataVisualization_production/(?P<id>.+)$', dataVisualization_production,name='dataVisualization_production.html'),
    url(r'^t/dataVisualization_judge/(?P<id>.+)$', dataVisualization_judge,name='dataVisualization_judge.html'),




    url(r'^t/import_student/$', import_student),
    # url(r'^t/class_management/$', ClassManagement),
    url(r'^t/class_management/$', ClassManagementList.as_view()),
    # url(r'^t/class_management/signup/$', ClassCreate.as_view()),
    url(r'^t/class_management_add/(?P<class_id>\w+)/$', ClassManagementAdd.as_view()),
    url(r'^t/class_management/(?P<class_id>\w+)/$', StudentManagementList.as_view(), name='class_management'),
    url(r'^t/class_management/(?P<class>\w+)/delete/$', ClassDelete.as_view()),
    url(r'^t/reset_student_password/(?P<student_pk>.+)/$', StudentManagementResetPassword.as_view()),
    url(r'^t/update_student/(?P<class_id>\w+)/(?P<pk>.+)/$', StudentManagementUpdate.as_view()),
    url(r'^t/update_student_all/(?P<pk>.+)/$', AllStudentManagementUpdate.as_view()),
    url(r'^t/delete_class_student/(?P<class_id>\w+)/(?P<pk>.+)/$', StudentDelte.as_view()),
    # url(r'^t/update_student/(?P<pk>\w+)/(?P<class_name>\w+)/$', StudentManagementUpdate.as_view()),
    url(r'^t/get_student/(?P<class_id>\w+)/(?P<target>\w+)/$', GetStudent.as_view()),
    url(r'^t/get_add_student/(?P<class_id>\w+)/(?P<target>\w+)/$', GetAddStudent.as_view()),
    url(r'^t/get_student_sousuo/(?P<target>\w+)/$', GetStudentSou.as_view()),
    url(r'^t/update_class/$', UpdateClassName),
    url(r'^t/add_student/$', StudentAddUpdate.as_view()),

    url(r'^t/import_student', import_student),
    url(r'^t/import_teacher', import_teacher),

    url(r'^t/get_course/(?P<target>\w+)/$', GetCourse.as_view()),
    url(r'^t/course_management/$', CourseList.as_view()),
    url(r'^t/course_management/new/$', CourseCreate.as_view()),
    url(r'^t/course_management/(?P<lesson>\w+)/$', CourseUpdate.as_view()),
    url(r'^t/course_management/(?P<lesson>\w+)/delete/$', CourseDelete.as_view()),

    url(r'^t/get_chapter/(?P<lesson>\w+)/(?P<target>\w+)/$', GetChapter.as_view()),
    url(r'^t/chapter_management/(?P<lesson>\w+)/$', ChapterList.as_view()),
    url(r'^t/chapter_management/(?P<lesson>\w+)/new/$', ChapterCreate.as_view()),
    url(r'^t/chapter_management/(?P<lesson>\w+)/(?P<chapter>\w+)/$', ChapterUpdate.as_view()),
    url(r'^t/chapter_management/(?P<lesson>\w+)/(?P<chapter>\w+)/delete/$', ChapterDelete.as_view()),

    # 竞赛管理

    url(r'^t/competition_management/$', CompetitionList.as_view()),
    url(r'^t/competition_management_adviser/$', CompetitionListAdviser.as_view()),
    url(r'^t/competition_management/(?P<pk>\w+)/delete/$', CompetitionDelete.as_view()),
    url(r'^t/compro_management/(?P<pk>\w+)/$', CompProducList.as_view()),
    url(r'^t/get_compro_management/(?P<pk>\w+)/$', GetCompProduc.as_view()),
    url(r'^t/compro_management_admin/(?P<pk>\w+)/$', CompProducAdminList.as_view()),
    url(r'^t/get_compro_management_admin/(?P<pk>\w+)/$', GetCompProducAdmin.as_view()),
    url(r'^t/compro_score_final/(?P<pk>\w+)/$', CompProScoreFinal.as_view()),
    url(r'^t/compro/(.+)/(.+)/$', scratch_api.teacher_views.comprograde, name='comprograde'),
    url(r'^t/import_competition_user', import_competition_user),
    url(r'^t/competition_management_admin/$', CompetitionListAdmin.as_view()),
    url(r'^t/competition_management_admin/new/$', CompetitionCreate.as_view()),
    url(r'^t/competition_management_admin/(?P<pk>\w+)/$', CompetitionUpdate.as_view()),
    url(r'^t/production_rater/',production_rater),
    url(r'^t/get_compro_user/(?P<pk>\w+)/(?P<target>\w+)/$',GetCompetitionUser.as_view()),
    url(r'^t/compro_management_user/(?P<pk>\w+)/$',CompetitionUserList.as_view()),
    url(r'^t/compro_management_user_update/(?P<competition>\w+)/(?P<user>\w+)/$',CompetitionUserUpdate.as_view()),
    url(r'^t/compro_management_adviser/(?P<pk>\w+)/$',CompProAdviserList.as_view()),
    url(r'^t/compro_progress/(?P<pk>\w+)/$',CompProgressList.as_view()),
    url(r'^t/get_compro_progress/(?P<pk>\w+)/(?P<target>\w+)/$', GetProgressList.as_view()),
    url(r'^t/compro_adviser/(.+)/(.+)/$', scratch_api.teacher_views.comprograde_adviser),
    url(r'^t/get_com_pro/(?P<pk>\w+)/$', GetComPro.as_view()),






    # url(r't/export_score/(?P<pk>\w+)/$',export_score),


    # 学生批量修改信息
    url(r'^t/student_list/',StudentList.as_view()),
    url(r'^t/get_list_student/',GetListStudent.as_view()),
    url(r'^t/updateschool/', updateschool),
    url(r'^t/updateclass/', updateclass),
    url(r'^t/alldelete_class_student/(?P<pk>.+)/$', AllStudentDelte.as_view()),

    # 教师管理
    url(r'^t/teacher_management/$', TeacherManagement),


    url(r'^t/passwordreset/',include(urls)),
    url(r'^t/resetpsw/',resetpwd),
    url(r't/competition_sign/',competition_sign),
    # url(r'^password_reset_recover/$', auth_views.password_reset, name='password_reset'),
    # url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.password_reset_confirm, name='password_reset_confirm'),
    # url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

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

    # NEW-教师端的URL
    url(r'^t/import_school/', import_school),
    url(r'^t/import_school_all/', import_school_all),
    url(r'^t/import_user/', import_user),
    url(r'^t/import_user_school/', import_user_school),
    url(r'^t/import_user_class/', import_user_class),
    url(r'^t/import_user_class_nadmin/', import_user_class_nadmin),
    url(r'^t/import_school_class/', import_school_class),
    url(r'^t/apply_management/', apply_management.as_view()),
    url(r'^t/apply_submit/$', apply_submit),
    url(r'^t/get_all_class/', get_all_class),
    url(r'^t/import_class_teacher/', import_class_teacher),
    url(r'^t/import_class/', import_class),
    url(r'^t/new_import_teacher/', new_import_teacher),
    url(r'^t/format_class_management/', format_class_management),
    url(r'^t/get_all_school/', get_all_school),
    url(r'^t/get_class/(?P<target>\w+)/$', GetClass.as_view()),
    url(r'^t/get_all_student/(?P<target>\w+)/', GetAllStudent.as_view()),
    url(r'^t/class_add_stu/', class_add_stu),



]
urlpatterns +=[
    # 以下url是首页的url

    url(r'^$', TemplateView.as_view(template_name='Scratch/index.html'), name="index"),
    url(r'^download/$', TemplateView.as_view(template_name='Scratch/download.html')),
    url(r'^downloadlist/$', WebsiteDownloadList.as_view()),
    # url(r'^lesson/$', TemplateView.as_view(template_name='Scratch/course.html')),
    url(r'^lesson/$', LessonListView.as_view()),
    url(r'^course_datil/$', get_side_course),
    url(r'^productlist/$', WebsiteProductionList.as_view()),
    url(r'^get_more_productions/$', MoreProductionListView.as_view()),
    # url(r'^myproductlist/$', WebsiteMyProductionList.as_view()),
    # url(r'^myclassproductlist/$', WebsiteMyClassProductionList.as_view()),
    url(r'^comments/', include('fluent_comments.urls')),
    url(r'^productdetail/(?P<id>.+)$', website_productiondetail, name='productiondetail'),
    url(r'^aboutus/$', TemplateView.as_view(template_name='Scratch/aboutus.html')),

    # url(r'^personal_center/$', TemplateView.as_view(template_name='Scratch/userpage.html')),
    # url(r'^myclassproductlist/$', WebsiteMyClassProductionList.as_view()),
    url(r'^change_password/$', StudentPasswordChangeView.as_view()),
    url(r'^website/login/$', website_login),
    url(r'^website/logout/$', website_logout),
    url(r'^website/ajax/favorite_production/(.+)/$', website_ajax_favorite),
    url(r'^website/ajax/like_production/(.+)/$', website_ajax_like),
    url(r'^website/remixtree/(?P<production>.+)/$', remix_tree, name='remixtree'),
    url(r'^website/remix/(?P<production>.+)/$', ProductionRemixList.as_view(), name='productionremix'),

    url(r'^website/ajax/comment_production/(.+)/$', website_ajax_comment_eachother),

    # url(r'^get_production_type_list/$', get_production_type_list),
    # url(r'^get_all_production/$', get_all_production),
]


urlpatterns += [
    # url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^ckeditor/upload/', (ckeditor_upload), name='ckeditor_upload'),
    url(r'^ckeditor/browse/', never_cache(staff_member_required(ckeditor_browse)), name='ckeditor_browse'),
    url(r'^course_info/TOC/$', TOCView.as_view()),
    url(r'^course/(?P<lesson>\w+)/$', get_lesson),
    url(r'^course/(?P<lesson>\w+)/(?P<chapter>\w+)/$', get_chapter),

    url(r'^course_info/(?P<lesson>\w+)/$', LessonView.as_view()),
    url(r'^course_info/(?P<lesson>\w+)/(?P<chapter>\w+)/$', ChapterView.as_view())
]

# 用户个人中心的url
urlpatterns +=[
    url(r'^userpage/(?P<author>.+)/$', WebsiteUserPage.as_view(), name='userpage'),
    url(r'^usersetting/(?P<pk>.+)/$', UserSetting.as_view(), name='usersetting'),
    url(r'^my_class/(?P<author>.+)$', WebsiteMyClass.as_view(), name='myclass'),
    url(r'^my_format_class/(?P<pk>.+)$', MyFormatClass.as_view(), name='myformatclass'),
    url(r'^get_class/$', get_classes),
    url(r'^get_format_classes/$', get_format_classes),
    url(r'^get_scname/$', truename_school),
    url(r'^get_format_scname/$', truename_format_school),
    url(r'^get_classname/$', truename_class),
    url(r'^get_format_classname/$', truename_format_class),
    url(r'^get_classmate_project_in_same_lesson/$', get_classmate_project_in_same_lesson),
    url(r'^addclass/$', StudentAddClass.as_view(),name='addclass'),
    url(r'^my_favorite/$', MyFavoriteList.as_view(), name='myfavorite'),
    url(r'^get_homework_project/$', get_homework_project),
    url(r'^get_teachers_score_and_comment_of_productions_by_ids/$',
        get_teachers_score_and_comment_of_productions_by_ids),
    url(r'^my_badge/$',TemplateView.as_view(template_name='test_badges.html')),

]

urlpatterns += [
    url(r'^notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^avatar/', include('avatar.urls')),
    url(r'^inbox/$', InboxUnreadList.as_view()),
    url(r'^inbox/all/$', InboxAllList.as_view()),
    url(r'^inbox/markreadall/$', website_inbox_readall),
    url(r'^inbox/detail/(?P<pk>.+)/$', InboxDeatil.as_view())
]

urlpatterns += [
    url(r'^qa/', include('qa.urls', namespace='qa')),
]

urlpatterns += [
    url(r'^OJ/', include('OJ.urls', namespace='OJ')),
]

urlpatterns += [
    url(r'^team_match/', include('team_match.urls', namespace='team_match')),
]

urlpatterns += [
    url(r'^util/', include('util.urls', namespace='util')),
]

urlpatterns += [
    url(r'^mobile_api/', include('mobile_api.urls', namespace='mobile_api')),
]

urlpatterns += [
    url(r'^behavior/', insert_behavior),
]

# 专题列表和详情
urlpatterns += [
    url(r'^gallerylist/$', WebsiteGalleryList.as_view()),
    url(r'^gallerydetail/(?P<id>.+)/$', WebsiteGalleryDetail.as_view(), name='gallerydetail'),
    url(r'^website/ajax/favorite_gallery/(.+)/$', website_ajax_gallery_favorite),
    url(r'^website/ajax/like_gallery/(.+)/$', website_ajax_gallery_like),
    url(r'^website_submitProductiontToGallery/(?P<user>.+)/(?P<gallery_id>.+)/$', website_submitProductiontToGallery, name='submitProductiontToGallery'),
    url(r'^submit_result/(?P<user>.+)/(?P<gallery_id>.+)/$',submit_result,name='submit_result'),
    url(r'^create_gallery/$', GalleryCreate.as_view(), name='create_gallery'),
]

urlpatterns += [
    url(r'^competition/$', CompetitionWebsiteList.as_view()),
    url(r'^competitions/(?P<title>.+)/$', CompetitionWebsiteDetail.as_view()),#目前已废弃
    url(r'^submit_competition/$', CompetitionWebsiteSubmit.as_view()),#目前已废弃
    url(r'^submit_competition_production/$', CompetitionWebsiteSubmitResult,name = 'CompetitionWebsiteSubmitResult'),#目前已废弃
    url(r'^competitionisover/$', CompetionIsOver)
]

# 权限管理
urlpatterns += [
    url(r'^t/permission_manage/$', GetTeacherTable.as_view()),
    url(r'^t/permission_manage_sousuo/(?P<target>\w+)/$', GetTeacher.as_view()),
    url(r'^t/change_teacher_permission/$', AllPermissions.as_view()),
    url(r'^t/change_teacher_permission_api/$', ChangeTeacherPermission.as_view()),
    url(r'^t/add_positions/$', AddPositions.as_view()),
    url(r'^t/check_positions/$', CheckPositions.as_view()),
    url(r'^t/check_one_position/$', CheckOnePositions.as_view()),
    url(r'^t/add_teacher_permission_api/$', AddTeacherPermission.as_view()),
]

# ajax传递作品操作时间
urlpatterns += [
    url(r'^scratch/ajax/liveTime`Sum/(?P<productionid>.+)/(?P<liveTimeSum>.+)/$', update_ajax_liveTimeSum,name='update_ajax_liveTimeSum'),
]

# 作品打分和展示
urlpatterns += [
    url(r'^BigData/local$', BigDataLocalJson.as_view()),
    # url(r'^BigData/data.json$', EchartsTest.as_view()),
    url(r'^BigData/online$', BigDataOnlineJson.as_view()),
    url(r'^BigData/ajax/favorite_gallery/$', get_json_online_test),

]
# urlpatterns += [
#     url(r'^test_badges/$', fucking_idots)
# ]




urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root='/static/')

urlpatterns += static("/scratch/", document_root='/static/')
urlpatterns += static("/scratch2/", document_root='scratch2')
