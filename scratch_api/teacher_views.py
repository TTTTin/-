# coding=utf-8
from __future__ import unicode_literals
from __future__ import division
import collections
import json
from collections import defaultdict

import xlwt
from io import BytesIO,StringIO
# from StringIO import StringIO
# from io import StringIO
# from StringIO import StringIO
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.contrib import messages
from django.core.paginator import PageNotAnInteger, Paginator
from django.forms import model_to_dict
from notifications.signals import notify

from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render_to_response, render, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.context_processors import csrf
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django_tables2 import RequestConfig, SingleTableView
from django.utils.http import urlquote
from rest_framework.generics import UpdateAPIView, ListAPIView
from rest_framework.views import APIView

from course.models import Lesson, Chapter
from scratch_api.mixins import CourseAuthorRequiredMixin,ProblemAuthorRequiredMixin,CompetitionUserAuthorRequiredMixin
from scratch_api.tables import ProdcutionTable,ProdcutionGradeTable, ProdcutionDownloadTable, ClassTable, UserTable,CourseTable,ChapterTable, ProblemTable, TestCasesTable
from scratch_api.mixins import CourseAuthorRequiredMixin,CompetitionAuthorRequiredMixin
from scratch_api.tables import ProdcutionTable, ProdcutionGradeTable, ProdcutionDownloadTable, ClassTable, UserTable, \
    CourseTable, ChapterTable, TeacherTable, CompetitionTable, ComProTable, CompetitionAdminTable, ComProAdminTable,CompetitionAdviserTable, \
    UserListTable,ComUserTable,ComProAdviserTable,ComProgressTable,ComProScoreTable
# from scratch_api.tasks import import_student_excel
# from util.excel import import_student_excel
from website.mixins import IsLoginMixin, AuthorRequiredMixin
from .models import Class, Teacher, School, User, Production, TeacherScore, CommentEachOther, ANTLRScore, \
    CompetitionUser, \
    ProductionHint, Production_profile, Position, Competition, CompetitionQuestion, QuestionProductionScore, Adviser, \
    FormatSchool, FormatClass
from .forms import MyAuthenticationForm, SignUpForm, UserUpdateForm, TeacherSettingForm
from gen.Gen import gen
from .tasks import import_student_excel, import_competition_user_excel, import_teacher_excel, upload_QuesProScore, \
    import_school_excel
from OJ.models import Problem, TestCase
from django.apps import apps
from guardian.shortcuts import remove_perm, assign_perm
from django.db.models import Q, Avg, Count, F, Case, When, FloatField, IntegerField


# import json


class MyLoginView(LoginView):
    """
    custom teacher login view
    """
    authentication_form = MyAuthenticationForm
    LOGIN_REDIRECT_URL = '/t/index'
    redirect_authenticated_user = True
    extra_context = {'class': "form-control"}


class MyPasswordChangeView(PasswordChangeView):
    success_url = '/accounts/password/'
    template_name = 'registration/password_change_form.html'

    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get a context
    #     context = super().get_context_data(**kwargs)
    #     # Add in the context
    #     context['name'] = Teacher.objects.get(pk=self.request.user).name
    #     context.update(csrf(self.request))
    #     if not Teacher.objects.filter(username__exact=self.request.user).first().position:
    #         context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
    #         if Position.objects.filter(name='普通教师'):
    #             Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
    #         else:
    #             p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
    #             Teacher.objects.get(username__exact=self.request.user).position = p
    #     else:
    #         context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
    #     return context


class StudentPasswordChangeView(PasswordChangeView):
    success_url = '/'
    template_name = 'Scratch/change_passowrd_form.html'

    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get a context
    #     context = super().get_context_data(**kwargs)
    #     # Add in the context
    #     try:
    #     context['name'] = BaseUser.objects.get(pk=self.request.user).name
    #     context.update(csrf(self.request))
    #     return context


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            teacher = Teacher.objects.get(username=username)
            format_school = request.POST.get("format_school", "")
            try:
                format_school = int(format_school)
                format_school = FormatSchool.objects.get(format_school)
                teacher.format_school = format_school
                teacher.save()
            except Exception as e:
                pass
            user = authenticate(username=username, password=raw_password)
            u = User(username=user, name=form.cleaned_data.get('name'))
            u.set_password(raw_password)
            u.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


class TeacherSetting(IsLoginMixin, AuthorRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherSettingForm
    template_name = 'teachersetting.html'

    def get_object(self, queryset=None):
        pk = self.kwargs['pk']
        return Teacher.objects.get(username=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        # 判断是否为老师
        try:
            # 关联（ select_realated ）position获取教师，只执行一次查库操作
            teacher = Teacher.objects.select_related("position").get(username__exact=pk)
        except Exception as e:
            context['no_access'] = "您不是老师，无权访问！"
            context['render_url'] = "/"
            return context

        context['name'] = teacher.name
        if not teacher.position:
            try:
                general_position = Position.objects.get(name="普通教师")
            except Exception:
                general_position = Position.objects.create(name="普通教师",
                                                           permission=Position.GENERAL_PERMISSION)
            teacher.position = general_position
            teacher.save()
        context['permissions'] = teacher.position.permissions
        return context

    def form_valid(self, form):
        
        return super(TeacherSetting, self).form_valid(form)

    def form_invalid(self, form):
        return super(TeacherSetting, self).form_invalid(form)

    def get_success_url(self):
        return reverse('teachersetting', kwargs={"pk": self.kwargs["pk"]})


def Personalsetting(request):
    return render(request,"registration/password_change_form.html")

class OrderList(SingleTableView):
    model = Chapter
    table_class = ChapterTable
    template_name = "chapter_management.html"

    def get_queryset(self):
        oup = self.request.GET.get('oup')
        odown=self.request.GET.get('odown')
        if oup:
            # print(oup)
            lesson_id = self.request.GET.get("lessonid")
            # print(lesson_id)
            lesson = Lesson.objects.filter(lesson_id=lesson_id)
            chapter = Chapter.objects.get(lesson=lesson, order=oup)
            chapter.up()
        elif odown:
            lesson_id=self.request.GET.get("lessonid")
            lesson = Lesson.objects.filter(lesson_id=lesson_id)
            chapter1 = Chapter.objects.get(lesson=lesson, order=odown)
            chapter1.up()
            # print(odown)
            # print(lesson_id)

        if lesson:
            sort = self.request.GET.get('sort')
            if sort:
                return Chapter.objects.filter(lesson=lesson).order_by(sort)
            else:
                return Chapter.objects.filter(lesson=lesson)



@login_required(login_url='/t/')
def sidebar(request):
    c = {}
    try:
        name = Teacher.objects.get(username__exact=request.user).name
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        name=""
    c['name'] = name
    if not Teacher.objects.filter(username__exact=request.user).first().position:
        c[
            'permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
        if Position.objects.filter(name='普通教师'):
            Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
        else:
            p = Position.objects.create(name='普通教师',
                                        permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
            Teacher.objects.get(username__exact=request.user).position = p
    else:
        c['permissions'] = Teacher.objects.filter(username__exact=request.user).first().position.permissions
    return render(request, "index.html", c)


@login_required(login_url='/')
def index(request):
    c = {}
    # 判断是否为老师
    try:
        # 关联（ select_realated ）position获取教师，只执行一次查库操作
        teacher = Teacher.objects.select_related("position").get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        c['render_url'] = "/"
        return render(request, 'index.html', c)
    c['name'] = teacher.name
    if not teacher.position:
        try:
            general_position = Position.objects.get(name="普通教师")
        except Exception:
            general_position = Position.objects.create(name="普通教师",
                                                       permissions=Position.GENERAL_PERMISSION)
        teacher.position = general_position
        teacher.save()

    # 获取 创建竞赛权限
    general_position = Position.objects.create(name="普通教师",permissions=Position.GENERAL_PERMISSION)
    teacher.position = general_position
    teacher.save()

    c['permissions'] = teacher.position.permissions
    c['name'] = teacher.name
    return render(request, "index.html", c)


@login_required(login_url='/')
def download(request):
    c = {}
    # 判断是否为老师
    try:
        # 关联（ select_realated ）position获取教师，只执行一次查库操作
        teacher = Teacher.objects.select_related("position").get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        c['render_url'] = "/"
        return render(request, 'download.html', c)

    c['name'] = teacher.name
    if not teacher.position:
        try:
            general_position = Position.objects.get(name="普通教师")
        except Exception :
            general_position = Position.objects.create(name="普通教师",
                                                       permission=Position.GENERAL_PERMISSION)
        teacher.position = general_position
        teacher.save()
    c['permissions'] = teacher.position.permissions
    # 判断权限中是否有查看作品列表的权限
    if not 'download_production' in teacher.position.permissions:
        c["no_access"] = "您没有权限查看该版块！"
        c['render_url'] = '/t/index'
        return render(request, 'download.html', c)

    format_classes = FormatClass.objects.filter(chief=teacher, is_active=True)
    c["format_classes"] = format_classes
    lessons = Lesson.objects.filter(Q(author=teacher) | Q(permission="PB"))
    c['lessons'] = lessons
    # ENF OF GET SCHOOL

    student = request.GET.get('student', "")
    work_name = request.GET.get('work_name', "")
    format_class_id = request.GET.get("format_class_id", "0")
    lesson_id = request.GET.get("lesson_id", "0")
    c["student"] = student
    c["work_name"] = work_name
    c["format_class_id"] = format_class_id
    c["lesson_id"] = lesson_id
    # 先获得全部课程下、非竞赛的作品
    productions = Production.objects.filter(format_class__in=format_classes, is_competition=False, is_active=True)
    # 根据查询的字段（课程id、班级id、学生姓名、学生用户名、作品名称）进行筛选
    if lesson_id and lesson_id != "0":
        productions = productions.filter(lesson=lesson_id)
    if format_class_id and format_class_id != "0":
        productions = productions.filter(format_class=format_class_id)
    if student and student != "":
        productions = productions.filter(Q(author__name__contains=student) | Q(author__username__contains=student))
    if work_name and work_name != "":
        productions = productions.filter(name=work_name)

    # 排序
    sort = request.GET.get("sort", "")
    if sort:
        try:
            if ("student" in sort) and not ("-student" in sort):
                productions = productions.order_by("author__name")
            elif "-student" in sort:
                productions = productions.order_by("-author__name")
            else:
                productions = productions.order_by(sort)
            c["sort"] = sort
        except Exception as e:
            pass
    # 翻页
    try:
        page = request.GET.get("page", 1)
    except PageNotAnInteger:
        page = 1
    c["page"] = page
    try:
        table = ProdcutionDownloadTable(productions)
        table.paginate(page=page, per_page=10)
        # RequestConfig(request, paginate={"per_page": 10}).configure(table)
        c['production_table'] = table
    except Exception as e:
        pass
    c.update(csrf(request))
    return render(request, 'download.html', c)

# 已废弃，功能挪至download中
# 废弃时间:2018-06-26
@login_required(login_url='/t/')
def grade(request):
    c = {}
    # TRY TO GET SCHOOL
    try:
        name = Teacher.objects.get(username__exact=request.user).name
        c['name'] = name

        if not Teacher.objects.filter(username__exact=request.user).first().position:
            c['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=request.user).position = p
        else:
            c['permissions'] = Teacher.objects.filter(username__exact=request.user).first().position.permissions

        # c['permissions'] = permissions
        teacher = Teacher.objects.get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        return render(request, 'list.html', c)
    class_ = Class.objects.filter(teacher=teacher)
    schools = class_.values('school_name').distinct()
    school_name = School.objects.filter(school_name__in=schools)
    c['schools'] = school_name
    lessons = Lesson.objects.filter(author=teacher)
    c['lessons'] = lessons
    # ENF OF GET SCHOOL

    school = request.GET.get('school', None)
    class_ = request.GET.get('class', None)
    student = request.GET.get('student', None)
    workname = request.GET.get('workname', None)
    lessonname = request.GET.get('lessonname', None)
    # if provide student
    if student:
        production = Production.objects.filter(author__exact=student).filter(is_active = True)
    # if provide class
    elif class_:
        class_=Class.objects.get(pk=class_)
        student = User.objects.filter(classes__exact=class_)
        production = Production.objects.filter(author__in=student)
    # if provide school
    elif school:
        class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)
        student = User.objects.filter(classes__in=class_)
        production = Production.objects.filter(author__in=student).filter(is_active = True)
    # provide nothing
    else:
        class_ = Class.objects.filter(teacher=teacher)
        student = User.objects.filter(classes__in=class_)
        # print(student)
        production = Production.objects.filter(author__in=student).filter(is_active = True)
        # filter by lesson name
    if lessonname and lessonname != "":
        lesson_ = Lesson.objects.filter(name__contains=lessonname)
        production = production.filter(lesson=lesson_).filter(is_active = True)
    # filter by production name
    if workname and workname != "":
        production = production.filter(name__contains=workname).filter(is_active = True)

    # 取出尚未评分的object
    # production = production.filter(teacherscore__isnull=True).filter(is_active = True)
    production = production.filter(~Q(name__icontains = "竞赛"))
    try:
        production = production.filter(is_competition=False)
        table = ProdcutionTable(production)
        RequestConfig(request, paginate={"per_page": 10}).configure(table)
        c['production_table'] = table
    except Exception:
        pass
    c.update(csrf(request))
    return render(request, 'grade.html', c)


def generate_dict_production(raw):

    result = {key: {'score':value, 'percentage': "{:.2f}".format(value/5*100)+"%" } for key, value in raw.items()}
    for key, value in result.items():
        if value['score'] == 0:
            value['class_name'] = 'progress-bar progress-bar-primary'
        elif value['score'] == 1:
            value['class_name'] = 'progress-bar progress-bar-primary'
        elif value['score'] == 2:
            value['class_name'] = 'progress-bar progress-bar-danger'
        elif value['score'] == 3:
            value['class_name'] = 'progress-bar progress-bar-warning'
        elif value['score'] == 4:
            value['class_name'] = 'progress-bar progress-bar-info'
        else:
            value['class_name'] = 'progress-bar progress-bar-success'
    result['ap_score']['name'] = '抽象和问题解决得分'
    result['user_interactivity_score']['name'] = '用户交互得分'
    result['data_representation_score']['name'] = '数据表示得分'
    result['logical_thinking_score']['name'] = '逻辑思维得分'
    result['parallelism_score']['name'] = '并行得分'
    result['synchronization_score']['name'] = '同步性得分'
    result['flow_control_score']['name'] = '顺序控制得分'
    # print(result)
    result['code_organization_score']['name'] = '代码组织得分'
    result['content_score']['name'] = '内容得分'
    return result


def generate_dict_test(raw):

    result = {key: {'score': value, 'percentage': "{:.2f}".format(value / 5 * 100) + "%"} for key, value in raw.items()}
    for key, value in result.items():
        if value['score'] == 0:
            value['class_name'] = 'progress-bar progress-bar-primary'
        elif value['score'] == 1:
            value['class_name'] = 'progress-bar progress-bar-primary'
        elif value['score'] == 2:
            value['class_name'] = 'progress-bar progress-bar-danger'
        elif value['score'] == 3:
            value['class_name'] = 'progress-bar progress-bar-warning'
        elif value['score'] == 4:
            value['class_name'] = 'progress-bar progress-bar-info'
        else:
            value['class_name'] = 'progress-bar progress-bar-success'
    result['ap_score']['name'] = '抽象和问题解决得分'
    result['user_interactivity_score']['name'] = '用户交互得分'
    result['data_representation_score']['name'] = '数据表示得分'
    result['logical_thinking_score']['name'] = '逻辑思维得分'
    result['parallelism_score']['name'] = '并行得分'
    result['synchronization_score']['name'] = '同步性得分'
    result['flow_control_score']['name'] = '顺序控制得分'
    # print(result)
    result['code_organization_score']['name'] = '代码组织得分'
    result['content_score']['name'] = '内容得分'
    return result


@login_required(login_url='/')
def production(request, id):
    c = {}
    try:
        # 关联（ select_realated ）position获取教师，只执行一次查库操作
        teacher = Teacher.objects.select_related("position").get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        c['render_url'] = "/"
        return render(request, 'production.html', c)

    c['name'] = teacher.name
    if not teacher.position:
        try:
            general_position = Position.objects.get(name="普通教师")
        except Exception :
            general_position = Position.objects.create(name="普通教师",
                                                       permission=Position.GENERAL_PERMISSION)
        teacher.position = general_position
        teacher.save()
    c['permissions'] = teacher.position.permissions
    # 判断权限中是否有打分的权限
    if not 'grade_production' in teacher.position.permissions:
        c["no_access"] = "您没有权限查看该版块！"
        c['render_url'] = '/t/index'
        return render(request, 'production.html', c)
    try:
        production = Production.objects.get(id=id)
        c['productionname'] =production.name
        c['url'] = production.file.url
        name = Teacher.objects.get(username__exact=request.user).name
        c['name'] = name
        c['production_id'] = production.id
    except Exception:
        return HttpResponseRedirect('/t/download/')
    # 判断该作品是否属于老师管辖范围内的班级的作品
    if production.format_class.chief != teacher:
        c["no_access"] = "您没有对此作品评分的权限"
        c["render_url"] = "/t/download/"
        return render(request, "production.html", c)
    if request.method == "POST":
        new_score = request.POST['new_score']
        new_comment = request.POST['new_comment']
        object = TeacherScore(production_id=production, score=int(new_score), comment=new_comment)
        object.save()
        return HttpResponse()

    if TeacherScore.objects.filter(production_id = production).exists():
        teacher_score = TeacherScore.objects.get(production_id__exact=id)
        c['teacher_score'] = teacher_score

    c['comment_eachother_all_score']=production.comment_eachother_all_score
    try:
        # print(id)
        # print(ANTLRScore.objects)
        antlr_score = ANTLRScore.objects.get(production_id=id)
        # print(antlr_score)
        score = model_to_dict(antlr_score, fields=['ap_score', 'parallelism_score', 'synchronization_score',
                                                   'flow_control_score', 'user_interactivity_score',
                                                   'logical_thinking_score', 'data_representation_score','content_score','code_organization_score'])
        # print(score)
        score_dict = generate_dict_production(score)
        c['antlr_score'] = score_dict
        total_score = sum(score.values())
        c['total_score'] = total_score
        production_hints = ProductionHint.objects.filter(production_id=id)
        c['production_hints'] = production_hints
        name = Teacher.objects.get(username__exact=request.user).name
        c['name'] = name


        antlr_profile = Production_profile.objects.get(production_id=id)
        profile = model_to_dict(antlr_profile, fields=['motion_num', 'looklike_num', 'sounds_num',
                                                       'draw_num', 'event_num',
                                                       'control_num', 'sensor_num', 'operate_num', 'more_num',
                                                       'data_num', 'sprite_num', 'backdrop_num', 'snd_num'])

        c['profiles'] = profile
    except Exception as e:
        # print(e)
        print("some error happen!")
    c.update(csrf(request))
    return render(request, 'production.html', c)


@login_required(login_url='/t/')
def list(request):
    c = {}
    # TRY TO GET SCHOOL
    try:
        name=Teacher.objects.get(username__exact=request.user).name
        c['name']=name
        teacher = Teacher.objects.get(username__exact=request.user)
        if not Teacher.objects.filter(username__exact=request.user).first().position:
            c['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=request.user).position = p
        else:
            c['permissions'] = Teacher.objects.filter(username__exact=request.user).first().position.permissions
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        return render(request, 'list.html', c)
    class_ = Class.objects.filter(teacher=teacher)
    schools = class_.values('school_name').distinct()
    school_name = School.objects.filter(school_name__in=schools)
    c['schools'] = school_name
    lessons = Lesson.objects.filter(author=teacher)
    c['lessons'] = lessons
    # ENF OF GET SCHOOL

    school = request.GET.get('school', None)
    class_ = request.GET.get('class', None)
    student = request.GET.get('student', None)
    workname = request.GET.get('workname', None)
    lessonname = request.GET.get('lessonname', None)
    # if provide student
    if student:
        production = Production.objects.filter(author__exact=student).filter(is_active = True)
    # if provide class
    elif class_:
        class_ = Class.objects.get(pk=class_)
        student = User.objects.filter(classes__exact=class_)
        production = Production.objects.filter(author__in=student).filter(is_active = True)
    # if provide school
    elif school:
        class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)
        student = User.objects.filter(classes__in=class_)
        production = Production.objects.filter(author__in=student).filter(is_active = True)
    # provide nothing
    else:
        class_ = Class.objects.filter(teacher=teacher)
        student = User.objects.filter(classes__in=class_)
        production = Production.objects.filter(author__in=student).filter(is_active = True)
    # filter by lesson name
    if lessonname and lessonname != "":
        lesson_ = Lesson.objects.filter(name__contains=lessonname)
        production = production.filter(lesson=lesson_).filter(is_active = True)
    # filter by production name
    if workname and workname != "":
        production = production.filter(name__contains=workname).filter(is_active = True)

    # 取出已经评分的object
    production = production.filter(teacherscore__isnull=False).filter(is_active = True)
    try:
        production = production.filter(is_competition=False)
        table = ProdcutionGradeTable(production)
        RequestConfig(request, paginate={"per_page": 10}).configure(table)
        c['production_table'] = table
    except Exception:
        pass
    c.update(csrf(request))
    return render(request, 'list.html', c)



@login_required(login_url='/')
def test(request):
    c = {}
    try:
        # 关联（ select_realated ）position获取教师，只执行一次查库操作
        teacher = Teacher.objects.select_related("position").get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        c['render_url'] = "/"
        return render(request, 'upload.html', c)
    c['name'] = teacher.name
    c.update(csrf(request))
    if not teacher.position:
        try:
            general_position = Position.objects.get(name="普通教师")
        except Exception :
            general_position = Position.objects.create(name="普通教师",
                                                       permission=Position.GENERAL_PERMISSION)
        teacher.position = general_position
        teacher.save()
    c['permissions'] = teacher.position.permissions
    # 判断权限中是否有查看作品列表的权限
    if not 'upload_test_production' in teacher.position.permissions:
        c["no_access"] = "您没有权限查看该版块！"
        c['render_url'] = '/t/index'
        return render(request, 'upload.html', c)
    if request.method == "POST":
        upload_file = request.FILES.get("myfile", None)
        if not upload_file:
            return HttpResponse("no files for upload!")
        s = BytesIO()
        for chunk in upload_file.chunks():
            s.write(chunk)
        try:
            score, hint,profile = gen(s)
            result = generate_dict_test(score)
            c['name']=Teacher.objects.get(username__exact=request.user).name
            c['filename']=upload_file
            c['antlr_score'] = result
            c['total_score'] = sum(score.values())
            c['production_hints'] = hint

        except Exception as e:
            c['error_happen'] = '很抱歉在测试的过程中发生了一些意外，请重试或联系管理员。' \
                                '请首先检查确保上传的文件为Scratch2的源代码文件'
            print("some error happen!")
        return render(request, "upload.html", c)
    else:
        return render(request, "upload.html", c)



@login_required(login_url='/t/')
def import_student(request):
    c = {}
    if request.method == "POST":
        upload_file = request.FILES.get("myfile", None)
        if not upload_file:
            return HttpResponse("no files for upload!")
        else:
            file=upload_file.read()
            c['name']=Teacher.objects.get(username__exact=request.user).name
            teacher = Teacher.objects.get(username__exact=request.user)
            import_student_excel.delay(file, teacher)
            c.update(csrf(request))
            return render(request, "import_student.html", c)
    else:
        c['name'] = Teacher.objects.get(username__exact=request.user).name

        if not Teacher.objects.filter(username__exact=request.user).first().position:
            c['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=request.user).position = p
        else:
            c['permissions'] = Teacher.objects.filter(username__exact=request.user).first().position.permissions

        c.update(csrf(request))
        return render(request, "import_student.html", c)

@login_required(login_url='/t/')
def import_teacher(request):
    c = {}
    if request.method == "POST":
        upload_file = request.FILES.get("myfile", None)
        if not upload_file:
            return HttpResponse("no files for upload!")
        else:
            file=upload_file.read()
            c['name']=Teacher.objects.get(username__exact=request.user).name
            teacher = Teacher.objects.get(username__exact=request.user)
            import_teacher_excel.delay(file, teacher)
            c.update(csrf(request))
            return render(request, "import_teacher.html", c)
    else:
        c['name'] = Teacher.objects.get(username__exact=request.user).name

        if not Teacher.objects.filter(username__exact=request.user).first().position:
            c['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=request.user).position = p
        else:
            c['permissions'] = Teacher.objects.filter(username__exact=request.user).first().position.permissions

        c.update(csrf(request))
        return render(request, "import_teacher.html", c)


@login_required(login_url='/t/')
def import_competition_user(request):
    c = {}
    if request.method == "POST":
        upload_file = request.FILES.get("myfile", None)
        if not upload_file:
            return HttpResponse("no files for upload!")
        else:
            file=upload_file.read()
            c['name']=Teacher.objects.get(username__exact=request.user).name
            teacher = Teacher.objects.get(username__exact=request.user)
            import_competition_user_excel.delay(file, teacher)
            c.update(csrf(request))
            return render(request, "import_competition_user.html", c)
    else:
        c['name'] = Teacher.objects.get(username__exact=request.user).name
        c.update(csrf(request))
        if not Teacher.objects.filter(username__exact=request.user).first().position:
            c['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=request.user).position = p
        else:
            c['permissions'] = Teacher.objects.filter(username__exact=request.user).first().position.permissions
            return render(request, "import_competition_user.html", c)

# def ClassManagement(request):
#     c = {}
#     # TRY TO GET SCHOOL
#     try:
#         teacher=Teacher.objects.get(username__exact=request.user)
#     except Exception as e:
#         c['no_access'] = "您不是老师，无权访问！"
#         return render_to_response('class_management.html', c)
#     c['name'] = Teacher.objects.get(username__exact=request.user).name
#
#     if not Teacher.objects.filter(username__exact=request.user).first().position:
#         c['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#         if Position.objects.filter(name='普通教师'):
#             Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
#         else:
#             p = Position.objects.create(name='普通教师',
#                                         permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#             Teacher.objects.get(username__exact=request.user).position = p
#     else:
#         c['permissions'] = Teacher.objects.filter(username__exact=request.user).first().position.permissions
#
#     class_ = Class.objects.filter(teacher=teacher)
#     schools = class_.values('school_name').distinct()
#     school_name = School.objects.filter(school_name__in=schools)
#     c['schools'] = school_name
#     # ENF OF GET SCHOOL
#
#     school = request.GET.get('school', None)
#     class1= request.GET.get('class', None)
#
#     # student = request.GET.get('student', None)
#     # workname = request.GET.get('workname', None)
#     if class1:
#         class_ = Class.objects.filter(teacher=teacher,school_name__exact=school ,id=class1)
#     elif school:
#         class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)
#
#     # provide nothing
#     # else:
#     #     class_ = Class.objects.filter(teacher=teacher)
#     # print(class_)
#
#     try:
#         table = ClassTable(class_)
#         RequestConfig(request, paginate={"per_page": 12}).configure(table)
#         c['class_table'] = table
#     except Exception:
#         pass
#     c.update(csrf(request))
#
#     return render(request, 'class_management.html', c)

# class ClassDelete(DeleteView):
#     template_name = "class_management_delete.html"
#     model=Class
#     success_url = '/t/class_management/'
#
#     def get_object(self, queryset=None):
#         try:
#             class_id = self.kwargs.get("class")
#             return Class.objects.get(id=class_id)
#         except Exception as e:
#             return None
#
#     def get_success_url(self):
#         return "/t/class_management/"
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context
# class ClassManagementList(SingleTableView):
#
#     model = Class
#     table_class = ClassTable
#     template_name = "class_management.html"
#
#     def get_queryset(self):
#         teacher = self.request.user
#         class_ = Class.objects.filter(teacher=teacher)
#         return class_
#
#     def get_table(self, **kwargs):
#         table = super().get_table()
#         RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
#         return table
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name']=Teacher.objects.get(username__exact=self.request.user).name
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context

# class ClassCreate(LoginRequiredMixin, CreateView):
#     # if you want to custom or modify default form, change form_class parameter
#     #     form_class = ContactForm
#     login_url = '/t/'
#     success_url = '/t/class_management/'
#     model = Class
#     template_name = "class_management_signup.html"
#     fields = ['school_name', 'class_name']
#
#     def form_valid(self, form):
#         # we need to add author field
#         response = super(ClassCreate, self).form_valid(form)
#         teacher = Teacher.objects.get(username=self.request.user)
#         self.object.teacher.add(teacher)
#         self.object.save()
#         return response
#
#     def form_invalid(self, form):
#         context = self.get_context_data(form=form)
#         context['error'] = "提交的信息有误，请检查后再提交"
#         return self.render_to_response(context)
#
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context

# class GetStudent(SingleTableView):
#     model = Class
#     table_class = UserTable
#     template_name = "student_management.html"
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['class_name'] = Class.objects.get(id=self.kwargs.get("class_id")).class_name
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context
#
#     def get_table(self, **kwargs):
#         table = super().get_table()
#         RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
#         return table
#
#     def get_queryset(self):
#         class_=Class.objects.filter(id=self.kwargs.get("class_id"),teacher=self.request.user)
#         if class_:
#             target = self.kwargs.get("target")
#             student = User.objects.filter(username=target,classes__in =class_)
#             return student
#         pass

def UpdateClassName(request):
    try:
        class_=Class.objects.get(id=request.GET.get('class_id'))
        class_.class_name=request.GET.get("target")
        class_.save()
        return redirect('/t/class_management')
    except Exception as e:
        return HttpResponse("班级名称已存在！")

class StudentAddUpdate(LoginRequiredMixin, CreateView):
    # if you want to custom or modify default form, change form_class parameter
    #     form_class = ContactForm
    login_url = '/t/'
    success_url = '/t/class_management/'
    model = User
    template_name = "student_add.html"
    fields = ['username', 'name', 'sex','classes', 'student_id', 'birthday', 'phone_number']

    def form_valid(self, form):
        # we need to add author field
        user = self.request.user
        teacher = Teacher.objects.get(username=user)
        form.instance.author = teacher
        return super(StudentAddUpdate, self).form_valid(form)
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context

# class StudentManagementList(SingleTableView):
#     model = Class
#     table_class = UserTable
#     template_name = "student_management.html"
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         context['class_name'] = Class.objects.get(id=self.kwargs.get("class_id")).class_name
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context
#
#     def get_table(self, **kwargs):
#         table = super().get_table()
#         RequestConfig(self.request, paginate=  {"per_page": 12}).configure(table)
#         return table
#
#     def get_queryset(self):
#         teacher = self.request.user
#         class_id = self.kwargs.get("class_id")
#         class_ = Class.objects.filter(teacher=teacher,id=class_id)
#         if class_:
#             student = User.objects.filter(classes__in=class_)
#             class_ = class_.first()
#         return student
# 学生批量修改信息列表
class StudentList(SingleTableView):
    model = User
    table_class = UserListTable
    template_name = "student_list.html"

    # def get_queryset(self):
    #     teacher = self.request.user
    #     stu_ = User.objects.all()
    #     return stu_
    #
    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        teacher = self.request.user
        student = User.objects.all()
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            student = student.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = UserListTable(student)
            table.paginate(page=page, per_page=10)
            context['student_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['name']=Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class GetListStudent(SingleTableView):
    model = User
    table_class = UserListTable
    template_name = "student_get.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] =Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
        return table

    def get_queryset(self):
        user = self.request.user
        school_ = self.request.GET.get('school', None)
        class_=self.request.GET.get('class',None)
        school1=School.objects.filter(school_name=school_)
        class1=Class.objects.filter(school_name=school1,class_name=class_)
        if school1.exists() and class1.exists():
            print(User.objects.filter(school__exact=school1).filter(classes__class_name__contains=class_))
            return User.objects.filter(school__exact=school1,classes__class_name__contains=class_).distinct()
        elif school1.exists():
            return User.objects.filter(school=school1)
        elif class1.exists():
            return User.objects.filter(classes__class_name__contains=class_)
        # production2question = {production: question for question in question_qs for production in
        #                        question.production.all()}
        # data = [{'id': production.id, 'question': question.question, 'competition': question.competition,
        #          'production': production.name,
        #          'score': QuestionProductionScore.objects.get(question=question, production=production,
        #                                                       rater=user).score if QuestionProductionScore.objects.filter(
        #              question=question, production=production, rater=user).exists() else None,
        #          'create_time': production.create_time} for production, question in production2question.items()]
        # # print(data)
        # username = tables.Column(verbose_name='用户名')
        # name = tables.Column(verbose_name="真实姓名")
        # sex = tables.Column(verbose_name="性别")
        # school = tables.Column(verbose_name="学校")
        # competition_id = self.kwargs.get("pk")
        # comp = Competition.objects.get(id=competition_id)
        # question_qs = CompetitionQuestion.objects.filter(competition=comp)
        # production2question = {production : question for question in question_qs for production in question.production.all()}
        # data = [{'id': production.id, 'question': question.question, 'competition': question.competition,'production': production.name,
        #          'score': QuestionProductionScore.objects.get(question=question, production=production, rater = user).score if QuestionProductionScore.objects.filter(question=question, production=production, rater = user).exists() else None,
        #          'create_time': production.create_time} for production, question in production2question.items()]
        # # print(data)
        # return data

def updateschool(request):
    if request.method == 'POST':
        ret = {'status': 1001}
        print(request.POST)
        usernames= request.POST.getlist('username[]')

        newschool=request.POST.get('newschool')
        if School.objects.filter(school_name=newschool).exists():
            school1=School.objects.get(school_name=newschool)
        else:
            school1=School(school_name=newschool)
            school1.save()
        try:
            for username in usernames:
                stu = User.objects.get(username=username)
                stu.school=school1
                stu.save()
        except Exception as e:
            print(e)
            ret = {'status': 1001}
        ret['status'] = 1002
        teacher = request.POST.get('')
        # notify.send(sender=teacher, recipient=teacher, actor=teacher,
        #             verb='批量修改学校名称成功', description='学生学校已修改为123456')
        return HttpResponse(json.dumps(ret))
    return render(request, 'student_get.html')
def updateclass(request):
    if request.method == 'POST':
        ret = {'status': 1001}
        usernames= request.POST.getlist('username[]')
        newclass=request.POST.get('newclass')
        newitem=newclass.split('的')
        newschool,created=School.objects.get_or_create(school_name=newitem[0])
        newschool.save()
        print(newitem[0])
        print(newschool)

        if Class.objects.filter(school_name=newschool,class_name=newitem[1]).exists():
            class1=Class.objects.get(school_name=newschool,class_name=newitem[1])
        else:
            class1 = Class(school_name=newschool, class_name=newitem[1])
            class1.save()
        try:
            for username in usernames:
                stu = User.objects.get(username=username)
                stu.classes.add(class1)
                stu.save()
        except Exception as e:
            print(e)
            ret = {'status': 1001}
        ret['status'] = 1002
        teacher = request.POST.get('')
        # notify.send(sender=teacher, recipient=teacher, actor=teacher,
        #             verb='批量修改学校名称成功', description='学生学校已修改为123456')
        return HttpResponse(json.dumps(ret))
    return render(request, 'student_get.html')
# class StudentManagementUpdate(UpdateView):
#     model = User
#     template_name = "student_management_update.html"
#     success_url = '/t/class_management/'
#     form_class = UserUpdateForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         # print(self.request.user)
#         # context['class_name']=self.kwargs.get("class_name")
#         # context['class_name'] = Class.objects.get(id=self.kwargs.get("class_id")).class_name
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context
    # def get_success_url(self):
    #     return reverse('class_management', kwargs={'pk': self.object.pk})


class StudentResetPassword(View):
    # context = {}

    def get(self, request, student_pk, *args, **kwargs):
        self.context = {}
        self.context['class_name']="学生班级"
        self.context.update(csrf(request))
        return render(request, "studentreset_password.html", self.context)

    def post(self, request, student_pk, *args, **kwargs):
        self.context = {}
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        print(password2)
        print(password1)
        if password1 and password2 and (password1 == password2):
            user = User.objects.get(pk=student_pk)
            user.set_password(password1)
            user.save()
            self.context["success"] = "重设成功"
        elif password1 != password2:
            self.context["error"] = "密码不匹配，请重新输入"
        self.context['name']=Teacher.objects.get(username__exact=self.request.user).name
        self.context['class_name']=self.kwargs.get("class_name")
        self.context.update(csrf(request))
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            self.context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            self.context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return render(request, "students_reset_password.html", self.context)

class StudentManagementResetPassword(View):
    # context = {}

    def get(self, request, student_pk, *args, **kwargs):
        self.context = {}
        self.context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        self.context['class_name']="学生班级"
        self.context.update(csrf(request))
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            self.context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            self.context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return render(request, "student_management_reset_password.html", self.context)

    def post(self, request, student_pk, *args, **kwargs):
        self.context = {}
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        print(password2)
        print(password1)
        if password1 and password2 and (password1 == password2):
            user = User.objects.get(pk=student_pk)
            user.set_password(password1)
            user.save()
            self.context["success"] = "重设成功"
        elif password1 != password2:
            self.context["error"] = "密码不匹配，请重新输入"
        self.context['name']=Teacher.objects.get(username__exact=self.request.user).name
        self.context['class_name']=self.kwargs.get("class_name")
        self.context.update(csrf(request))
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            self.context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            self.context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return render(request, "student_management_reset_password.html", self.context)


class StudentDelte(DeleteView):
    template_name = "student_management_delete.html"
    model = User
    # class_id = render()
    success_url = '/t/class_management/'

    def get_object(self, queryset=None):
        try:
            username = self.kwargs.get("pk")
            return User.objects.get(username=username)
        except Exception as e:
            return None

    def post(self, request, *args, **kwargs):
        class_id=self.kwargs.get("class_id")
        # print(class_id)
        username=self.kwargs.get("pk")
        user = User.objects.get(username=username)
        user.format_class.remove(class_id)
        user.save()
        return HttpResponseRedirect('/t/class_management/'+class_id+'/')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class AllStudentDelte(DeleteView):
    template_name = "all_student_management_delete.html"
    model = User
    # class_id = render()
    success_url = '/t/student_list/'

    def get_object(self, queryset=None):
        try:
            username = self.kwargs.get("pk")
            return User.objects.get(username=username)
        except Exception as e:
            return None

    def post(self, request, *args, **kwargs):
        # print(class_id)
        username=self.kwargs.get("pk")
        user = User.objects.get(username=username)
        user.delete()
        return HttpResponseRedirect('/t/student_list/')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class CourseList(SingleTableView):
    model = Lesson
    table_class = CourseTable
    template_name = "course_management.html"

    # def get_queryset(self):
    #     user = self.request.user
    #     return Lesson.objects.filter(author=user)
    #
    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        user = self.request.user
        lesson = Lesson.objects.filter(author=user)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            lesson = lesson.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = CourseTable(lesson)
            table.paginate(page=page, per_page=10)
            context['lesson_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions

        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions

        return context


class GetCourse(SingleTableView):
    model = Lesson
    table_class = CourseTable
    template_name = "course_management.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # target = self.request.GET.get('target', None)
        target = self.kwargs.get("target")
        lesson = Lesson.objects.filter(author=user).filter(name=target)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            lesson = lesson.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = CourseTable(lesson)
            table.paginate(page=page, per_page=10)
            context['lesson_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['name'] =Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context

    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table
    #
    # def get_queryset(self):
    #     user = self.request.user
    #     target = self.request.GET.get('target', None)
    #     return Lesson.objects.filter(author=user).filter(name=target)


class CourseCreate(LoginRequiredMixin, CreateView):
    # if you want to custom or modify default form, change form_class parameter
    #     form_class = ContactForm
    login_url = '/t/'
    success_url = '/t/course_management/'
    model = Lesson
    template_name = "course_management_new.html"
    fields = ['name', 'classes', 'author', 'introduction', 'task', 'short_introduction', 'audio', 'image', 'permission']

    def form_valid(self, form):
        # we need to add author field
        user = self.request.user
        teacher = Teacher.objects.get(username=user)
        form.instance.author = teacher
        return super(CourseCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class CourseUpdate(CourseAuthorRequiredMixin, UpdateView):
    login_url = '/t/'
    model = Lesson
    fields = ['name', 'classes', 'author', 'introduction', 'task', 'short_introduction', 'audio', 'image', 'permission']
    template_name = "course_management_update.html"
    success_url = '/t/course_management/'

    def get_object(self, queryset=None):
        try:
            lesson_id = self.kwargs.get("lesson")
            return Lesson.objects.get(lesson_id=lesson_id)
        except Exception as e:
            return None

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class CourseDelete(DeleteView):
    template_name = "course_management_delete.html"
    model = Lesson
    success_url = '/t/course_management/'

    def get_object(self, queryset=None):
        try:
            lesson_id = self.kwargs.get("lesson")
            return Lesson.objects.get(lesson_id=lesson_id)
        except Exception as e:
            return None

    def get_success_url(self):
        return "/t/course_management/"
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context

class ChapterList(SingleTableView):
    model = Chapter
    table_class = ChapterTable
    template_name = "chapter_management.html"

    # def get_queryset(self):
    #     lesson_id = self.kwargs.get("lesson")
    #     lesson = Lesson.objects.filter(lesson_id=lesson_id)
    #     if lesson:
    #         sort = self.request.GET.get('sort')
    #         if sort:
    #             return Chapter.objects.filter(lesson=lesson).order_by(sort)
    #         else:
    #             return Chapter.objects.filter(lesson=lesson)
    #         # user = self.request.user
    #         # return Lesson.objects.filter(author=user)
    #
    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        lesson_id = self.kwargs.get("lesson")
        lesson = Lesson.objects.filter(lesson_id=lesson_id)
        if lesson:
            chapter = Chapter.objects.filter(lesson=lesson)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            chapter = chapter.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = ChapterTable(chapter)
            table.paginate(page=page, per_page=10)
            context['chapter_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        context['lesson_id'] = self.kwargs.get("lesson")
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context[
                'permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师',
                                            permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(
                username__exact=self.request.user).first().position.permissions
        return context

class GetChapter(SingleTableView):
    model = Chapter
    table_class = ChapterTable
    template_name = "chapter_management.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # target = self.request.GET.get('target', None)
        target = self.kwargs.get("target")
        lesson_id = self.kwargs.get("lesson")
        lesson = Lesson.objects.filter(lesson_id=lesson_id)
        if lesson:
            chapter = Chapter.objects.filter(lesson=lesson).filter(name=target)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            chapter = chapter.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = ChapterTable(chapter)
            table.paginate(page=page, per_page=10)
            context['chapter_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        context['lesson_id'] = self.kwargs.get("lesson")
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context

    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table
    #
    # def get_queryset(self):
    #     target = self.request.GET.get('target', None)
    #     lesson_id = self.kwargs.get("lesson")
    #     lesson = Lesson.objects.filter(lesson_id=lesson_id)
    #     if lesson:
    #         return Chapter.objects.filter(lesson=lesson).filter(name=target)


class ChapterCreate(CourseAuthorRequiredMixin, CreateView):
    login_url = '/t/'
    model = Chapter
    template_name = "chapter_management_new.html"
    fields = ['lesson', 'chapter_id', 'name', 'content', 'audio']
    success_url = '/t/course_management/'

    # def form_valid(self, form):
    #     try:
    #         # we need to add lesson field
    #         lesson = Lesson.objects.get(lesson_id=self.kwargs.get("lesson"))
    #         chapter_id = Chapter.objects.filter(lesson=lesson).count() + 1
    #         form.instance.lesson = lesson
    #         form.instance.chapter_id = chapter_id
    #         return super(ChapterCreate, self).form_valid(form)
    #     except Exception as e:
    #         return super(ChapterCreate, self).form_invalid(form)
    #
    # def form_invalid(self, form):
    #     return super(ChapterCreate, self).form_invalid(form)

    def get_success_url(self):
        return "/t/chapter_management/" + self.kwargs.get("lesson") + '/?sort=order'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name

        lesson_id = self.kwargs.get("lesson")
        lesson = Lesson.objects.get(lesson_id=lesson_id)
        context['lesson']=lesson
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class ChapterUpdate(CourseAuthorRequiredMixin, UpdateView):
    login_url = '/t/'
    model = Chapter
    fields = ['lesson', 'chapter_id', 'name', 'content', 'audio']
    template_name = "chapter_management_update.html"

    def get_object(self, queryset=None):
        try:
            lesson_id = self.kwargs.get("lesson")
            lesson = Lesson.objects.get(lesson_id=lesson_id)
            if lesson:
                chapter_id = self.kwargs.get("chapter")
                return Chapter.objects.get(lesson=lesson, chapter_id=chapter_id)
        except Exception as e:
            return None

    def get_success_url(self):
        return "/t/chapter_management/" + self.kwargs.get("lesson") + '/?sort=order'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class ChapterDelete(DeleteView):
    template_name = "chapter_management_delete.html"
    model = Lesson

    def get_object(self, queryset=None):
        try:
            lesson_id = self.kwargs.get("lesson")
            lesson = Lesson.objects.get(lesson_id=lesson_id)
            if lesson:
                chapter_id = self.kwargs.get("chapter")
                # print(Chapter.objects.get(lesson=lesson, chapter_id=chapter_id))
                return Chapter.objects.get(lesson=lesson, chapter_id=chapter_id)
        except Exception as e:
            return None

    def get_success_url(self):
        return "/t/chapter_management/" + self.kwargs.get("lesson") + '/?sort=order'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context[
                'permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师',
                                            permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(
                username__exact=self.request.user).first().position.permissions
        return context
#教师管理
def TeacherManagement(request):
    c = {}
    # TRY TO GET SCHOOL
    try:
        teacher=Teacher.objects.get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        return render_to_response('teacher_management.html', c)
    c['name'] = Teacher.objects.get(username__exact=request.user).name

    if not Teacher.objects.filter(username__exact=request.user).first().position:
        c['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
        if Position.objects.filter(name='普通教师'):
            Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
        else:
            p = Position.objects.create(name='普通教师',
                                        permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
            Teacher.objects.get(username__exact=request.user).position = p
    else:
        c['permissions'] = Teacher.objects.filter(username__exact=request.user).first().position.permissions

    class_ = Class.objects.filter(teacher=teacher)
    # schools = class_.values('school_name').distinct()
    # school_name = School.objects.filter(school_name__in=schools)
    # c['schools'] = school_name
    # # ENF OF GET SCHOOL
    #
    # school = request.GET.get('school', None)
    # class1= request.GET.get('class', None)
    # # print(class1)
    # # student = request.GET.get('student', None)
    # # workname = request.GET.get('workname', None)
    # if class1:
    #     class_ = Class.objects.filter(teacher=teacher,school_name__exact=school ,id=class1)
    # elif school:
    #     class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)

    # provide nothing
    # else:
    #     class_ = Class.objects.filter(teacher=teacher)
    # print(class_)

    try:
        table = ClassTable(class_)
        RequestConfig(request, paginate={"per_page": 12}).configure(table)
        c['class_table'] = table
    except Exception:
        pass
    c.update(csrf(request))

    return render(request, 'teacher_management.html', c)
# 竞赛


class CompetitionList(SingleTableView):
    model = Competition
    table_class = CompetitionTable
    template_name = "competition_management.html"

    # def get_queryset(self):
    #     user = self.request.user
    #     return Competition.objects.filter(rater=user)
    #
    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #
    #     return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        user = self.request.user
        competition = Competition.objects.filter(rater=user)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            competition = competition.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = CompetitionTable(competition)
            table.paginate(page=page, per_page=10)
            context['competition2_table'] = table

        except Exception as e:
            pass
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions

        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions

        return context

# 竞赛更新
class CompetitionUpdate(CompetitionAuthorRequiredMixin, UpdateView):
    login_url = '/t/'
    model = Competition
    fields = ['title', 'creator', 'rater', 'advisers', 'start_time', 'stop_time', 'content']
    template_name = "competition_management_update.html"
    success_url = '/t/competition_management_admin/'

    def get_object(self, queryset=None):
        try:
            com_pk = self.kwargs.get("pk")
            return Competition.objects.get(pk=com_pk)
        except Exception as e:
            print(e)
            return None

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context

# 竞赛删除
class CompetitionDelete(DeleteView):
    template_name = "competition_management_delete.html"
    model = Competition
    success_url = '/t/competition_management_admin/'

    def get_object(self, queryset=None):
        try:
            com_pk = self.kwargs.get("pk")
            return Competition.objects.get(pk=com_pk)
        except Exception as e:
            print(e)
            return None

    def get_success_url(self):
        return "/t/competition_management_admin/"
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class CompetitionListAdmin(SingleTableView):
    model = Competition
    table_class = CompetitionAdminTable
    template_name = "competition_management_admin.html"

    # def get_queryset(self):
    #     user = self.request.user
    #     return Competition.objects.filter(creator=user)
    #
    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #
    #     return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        user = self.request.user
        competition = Competition.objects.filter(creator=user)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            competition = competition.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = CompetitionAdminTable(competition)
            table.paginate(page=page, per_page=10)
            context['competition_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions

        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions

        return context


class CompProducList(SingleTableView):
    model = CompetitionQuestion
    table_class = ComProTable
    template_name = "compro_management.html"

    def get_queryset(self):
        user = self.request.user
        competition_id = self.kwargs.get("pk")
        comp = Competition.objects.get(id=competition_id)
        qs = QuestionProductionScore.objects.filter(rater=user, question__in=CompetitionQuestion.objects.filter(competition=comp))
        data = [{'id': item.production.id, 'question': item.question.question, 'competition': item.question.competition, 'production': item.production.name,
                 'score': QuestionProductionScore.objects.get(question=item.question, production=item.production, rater=user).score if QuestionProductionScore.objects.filter(question=item.question, production=item.production, rater = user).exists() else None,
                 'ct_score': ANTLRScore.objects.get(production_id=item.production.id).total if ANTLRScore.objects.filter(production_id=item.production.id).exists() else None,
                 'create_time': item.production.create_time,
                 'limit_score':item.question.limit_score} for item in qs]
        return data

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # 排序
        sort = self.request.GET.get("sort", "")
        context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        # Add in the context
        competition_id = self.kwargs.get("pk")
        context['pk'] = competition_id
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions

        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class GetCompProduc(SingleTableView):
    model = CompetitionQuestion
    table_class = ComProTable
    template_name = "compro_management.html"

    def get_queryset(self):
        target = self.request.GET.get('target', None)
        user = self.request.user
        competition_id = self.kwargs.get("pk")
        comp = Competition.objects.get(id=competition_id)
        pro = Production.objects.filter(id=target)
        # pro = Production.objects._mptt_filter(id=target)
        qs = QuestionProductionScore.objects.filter(rater=user, question__in=CompetitionQuestion.objects.filter(competition=comp),production=pro)
        data = [{'id': item.production.id, 'question': item.question.question, 'competition': item.question.competition, 'production': item.production.name,
                 'score': QuestionProductionScore.objects.get(question=item.question, production=item.production, rater=user).score if QuestionProductionScore.objects.filter(question=item.question, production=item.production, rater = user).exists() else None,
                 'ct_score': ANTLRScore.objects.get(production_id=item.production.id).total if ANTLRScore.objects.filter(production_id=item.production.id).exists() else None,
                 'create_time': item.production.create_time,
                 'limit_score':item.question.limit_score} for item in qs]
        return data

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        competition_id = self.kwargs.get("pk")
        context['pk'] = competition_id
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions

        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class CompProScoreFinal(TemplateView):

    template_name = "compro_score_final.html"

    def get_data(self):
        competition_id = self.kwargs.get("pk")
        comp = Competition.objects.get(id=competition_id)
        question_set = CompetitionQuestion.objects.filter(competition=comp)
        qs = QuestionProductionScore.objects.filter(question__in=question_set)

        # 首先取出参加此次竞赛的所有user,同时取出user的导师、真实姓名和学校
        name_list = CompetitionUser.objects.filter(competition=comp).values('user').annotate(tutor_name=F('tutor__name'), name=F('user__name'), school=F('user__format_school__name'))

        #因为ValuesQuerySet无法序列化，我们这里需要手动将其转为List
        data = []
        for user_item in name_list:
            #用户的最终得分首先设置为0
            user_item['total_score'] = 0
            #detail里保存每道题的详细得分
            user_item['detail'] = []

            #取出该作者的所有题目，并标注其评委的给的评分得分、教研员给的得分、CT得分和所属问题
            productions = QuestionProductionScore.objects.filter(production__author=user_item['user'], question__competition=comp).values('production').\
                annotate(rater_avg_score=Avg(Case(When(is_adviser=False, then='score'), output_field=FloatField())),
                         adviser_score=Avg(Case(When(is_adviser=True, then='score'), output_field=IntegerField())),
                         CT_score=F('production__antlrscore__total'),
                         question=F('question__question'),
                         )
            for production in productions:
                question_score = []
                #UUID无法序列化，这里将其转为string
                production['production'] = str(production['production'])
                #将题目详情加到作者的detail
                user_item['detail'].append(production)
                #将该题的最终得分加到该作者的题目总得分上去
                if production['adviser_score']:
                    user_item['total_score'] += production['adviser_score']
                    
                elif production['rater_avg_score']:
                    user_item['total_score'] += production['rater_avg_score']

            data.append(user_item)

        rater_qs = qs.filter(is_adviser=False)

        #取出每道题各个评委打分详情
        production2score = {}
        for item in rater_qs:
            production_pk = str(item.production_id)
            if production_pk in production2score:
                if item.score !=None:
                    production2score[production_pk] += ";" + str(item.rater.name) + ":" + str(item.score) + "分"
                else:
                    production2score[production_pk] += "; " + str(item.rater.name) + ":未评分"
            else:
                if item.score!=None:
                    production2score[production_pk] = str(item.rater.name) + ":" + str(item.score) + "分"
                else:
                    production2score[production_pk] = str(item.rater.name) + ":未评分"

        return data, production2score

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        list, production2score = self.get_data()
        context['list'] = json.dumps(list)
        context['production2score'] = json.dumps(production2score)
        context['competition_name'] = Competition.objects.get(id= self.kwargs.get("pk")).title

        # ?这下面有用吗
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        competition_id = self.kwargs.get("pk")
        context['pk']=competition_id
        context['raters'] = Competition.objects.get(id=competition_id).rater
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions

        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class CompProducAdminList(SingleTableView):
    model = CompetitionQuestion
    table_class = ComProAdminTable
    template_name = "compro_management_admin.html"

    def get_queryset(self):
        user = self.request.user
        competition_id = self.kwargs.get("pk")
        comp = Competition.objects.get(id=competition_id)
        question_qs = CompetitionQuestion.objects.filter(competition=comp)
        production2question = {production : question for question in question_qs for production in question.production.all()}
        data = [{'name':production.author,'id': production.id, 'question': question.question, 'competition': question.competition,'production': production.name,
                'create_time': production.create_time,
                 'limit_score':question.limit_score} for production, question in production2question.items()]
        # print(data)
        return data

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # 排序
        sort = self.request.GET.get("sort", "")
        context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        competition_id = self.kwargs.get("pk")
        context['pk']=competition_id
        context['raters'] = Competition.objects.get(id=competition_id).rater
        print(Competition.objects.get(id=competition_id).rater)
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions

        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class GetCompProducAdmin(SingleTableView):
    model = CompetitionQuestion
    table_class = ComProAdminTable
    template_name = "compro_management_admin.html"

    def get_queryset(self):
        target = self.request.GET.get('target', None)
        user = self.request.user
        competition_id = self.kwargs.get("pk")
        print(competition_id)
        comp = Competition.objects.get(id=competition_id)
        question_qs = CompetitionQuestion.objects.filter(competition=comp)
        production2question = {production : question for question in question_qs for production in question.production.filter(id=target)}
        data = [{'name':production.author,'id': production.id, 'question': question.question, 'competition': question.competition,'production': production.name,
                'create_time': production.create_time,
                 'limit_score':question.limit_score} for production, question in production2question.items()]
        # print(data)
        return data

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        competition_id = self.kwargs.get("pk")
        context['pk']=competition_id
        context['raters'] = Competition.objects.get(id=competition_id).rater
        print(Competition.objects.get(id=competition_id).rater)
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions

        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class GetCompetitionUser(SingleTableView):
    model = CompetitionUser
    table_class = ComUserTable
    template_name = "compro_management_user.html"

    # def get_queryset(self):
    #     target = self.request.GET.get('target', None)
    #     competition_id=self.kwargs.get("pk")
    #     print(competition_id)
    #     print(target)
    #     comp=Competition.objects.get(id=competition_id)
    #     return CompetitionUser.objects.filter(competition=comp,user=target)
    #
    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        target = self.kwargs.get("target")
        # target = self.request.GET.get('target', None)
        competition_id=self.kwargs.get("pk")
        comp=Competition.objects.get(id=competition_id)
        competition = CompetitionUser.objects.filter(competition=comp,user=target)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            competition = competition.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = ComUserTable(competition)
            table.paginate(page=page, per_page=10)
            context['competition1_table'] = table
        except Exception as e:
            pass
        # Add in the context
        competition_id = self.kwargs.get("pk")
        title_ = Competition.objects.get(id=competition_id).title
        context['pk']=competition_id
        context['title']=title_
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class CompetitionUserList(SingleTableView):
    model = CompetitionUser
    table_class = ComUserTable
    template_name = "compro_management_user.html"

    # def get_queryset(self):
    #     competition_id=self.kwargs.get("pk")
    #     print(competition_id)
    #     comp=Competition.objects.get(id=competition_id)
    #     return CompetitionUser.objects.filter(competition=comp)
    #
    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        competition_id = self.kwargs.get("pk")
        comp = Competition.objects.get(id=competition_id)
        competition = CompetitionUser.objects.filter(competition=comp)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            competition = competition.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = ComUserTable(competition)
            table.paginate(page=page, per_page=10)
            context['competition1_table'] = table
        except Exception as e:
            pass
        # Add in the context
        competition_id = self.kwargs.get("pk")
        title_=Competition.objects.get(id=competition_id).title
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions
        context['pk']=competition_id
        context['title']=title_
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class CompetitionUserUpdate(CompetitionUserAuthorRequiredMixin, UpdateView):
    login_url = '/t/'
    model = CompetitionUser
    fields = ['competition', 'user', 'tutor', 'delay_time']
    template_name = "compro_management_user_update.html"

    def get_object(self, queryset=None):
        try:
            competition_user = self.kwargs.get("user")
            user_ = User.objects.get(username=competition_user)
            return CompetitionUser.objects.get(user=user_)
        except Exception as e:
            print(e)
            return None

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        competition = self.kwargs.get("competition")
        context['competition'] = competition
        # competition = CompetitionUser.objects.get(user=user).competition_id
        # user_= CompetitionUser.objects.get(user=user).user
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context

    def get_success_url(self):
        return "/t/compro_management_user/" + self.kwargs.get("competition")+"/"


def production_rater(request):
    if request.method == 'POST':
        ret = {'status': 1000}
        production = request.POST.get('production')
        production1 = json.loads(production)
        options1 = request.POST.get('options')
        options = json.loads(options1)
        if len(production1):
            pass
        else:
            ret = {'status': 1001}
        if len(options):
            pass
        else:
            ret = {'status': 1002}

        print(options)
        try:
            for production_ in production1:
                for option in options:
                    pro = Production.objects.get(id=production_)
                    rater_ = Teacher.objects.get(username=option)
                    ques = CompetitionQuestion.objects.get(production=pro)
                    if QuestionProductionScore.objects.filter(question=ques, production=pro, rater=rater_).exists():
                        ret = {'status': 1005}
                    else:
                        raterpro = QuestionProductionScore(question=ques, production=pro, rater=rater_)
                        raterpro.save()
                        ret = {'status': 1004}
        except Exception as e:
            ret = {'status': 1003}
        return HttpResponse(json.dumps(ret))
    return render(request, 'compro_management_admin.html')

@login_required(login_url='/t/')
def comprograde(request,question, id):
    c = {}
    try:
        question = CompetitionQuestion.objects.get(question=question)
        production = Production.objects.get(id=id)
        c['productionname'] = production.name
        c['pk'] = question.competition_id
        c['url'] = production.file.url
        c['description'] = production.description
        c['operation_instructions'] = production.operation_instructions
        c['production_id'] = production.id
        c['limit_score'] = question.limit_score
        c['limit_small_score'] = question.limit_small_score
        name = Teacher.objects.get(username__exact=request.user).name
        c['name'] = name
    except Exception as e:
        return HttpResponseRedirect('/index/')
    if request.method == "POST":

        integrity_score = request.POST['integrity_score']
        technical_score = request.POST['technical_score']
        artistry_score = request.POST['artistry_score']
        creativity_score = request.POST['creativity_score']
        total_score = int(integrity_score) + int(technical_score) + int(artistry_score) + int(creativity_score)
        new_comment = request.POST['new_comment']
        small_score = {
            "创造性": creativity_score,
            "完整性": integrity_score,
            "艺术性": artistry_score,
            "技术性": technical_score,
        }
        if QuestionProductionScore.objects.filter(question=question, production=production,
                                                  rater=Teacher.objects.get(username__exact=request.user)).exists():
            qss = QuestionProductionScore.objects.get(question=question,
                                                      rater=Teacher.objects.get(username__exact=request.user),
                                                      production=production)

            qss.small_score = small_score
            qss.score = int(total_score)
            qss.save()
            qsc = QuestionProductionScore.objects.get(question=question,
                                                rater=Teacher.objects.get(username__exact=request.user),
                                                production=production)
            qsc.comment = new_comment
            qsc.save()
            upload_QuesProScore.delay(qsc.id)
        else:
            object = QuestionProductionScore(question=question, production=production,
                                             rater=Teacher.objects.get(username__exact=request.user),score=int(total_score), small_score=small_score, comment=new_comment)

            object.save()

    if QuestionProductionScore.objects.filter(question=question,rater=Teacher.objects.get(username__exact=request.user),
                                              production= production).exists():
        teacher_score = QuestionProductionScore.objects.get(question=question,rater=Teacher.objects.get(username__exact=request.user),
                                                            production=production)
        c['teacher_score'] = teacher_score
    try:
        # print(id)
        # print(ANTLRScore.objects)
        antlr_score = ANTLRScore.objects.get(production_id=id)
        # print(antlr_score)
        score = model_to_dict(antlr_score, fields=['ap_score', 'parallelism_score', 'synchronization_score',
                                                   'flow_control_score', 'user_interactivity_score',
                                                   'logical_thinking_score', 'data_representation_score','content_score','code_organization_score'])
        # print(score)
        score_dict = generate_dict_production(score)
        c['antlr_score'] = score_dict
        total_score = sum(score.values())
        c['total_score'] = total_score
        production_hints = ProductionHint.objects.filter(production_id=id)
        c['production_hints'] = production_hints
        name = Teacher.objects.get(username__exact=request.user).name
        c['name'] = name

        antlr_profile = Production_profile.objects.get(production_id=id)
        profile = model_to_dict(antlr_profile, fields=['motion_num', 'looklike_num', 'sounds_num',
                                                       'draw_num', 'event_num',
                                                       'control_num', 'sensor_num', 'operate_num', 'more_num',
                                                       'data_num', 'sprite_num', 'backdrop_num', 'snd_num'])
        c['profiles'] = profile
    except Exception as e:
        print("some error happen!")
    c.update(csrf(request))
    if not Teacher.objects.filter(username__exact=request.user).first().position:
        c['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
        if Position.objects.filter(name='普通教师'):
            Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
        else:
            p = Position.objects.create(name='普通教师',
                                        permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
            Teacher.objects.get(username__exact=request.user).position = p
    else:
        c['permissions'] = Teacher.objects.filter(username__exact=request.user).first().position.permissions
    return render(request, 'comprograde.html', c)


@login_required(login_url='/t/')
def comprograde_adviser(request,question, id):
    c = {}
    try:
        question=CompetitionQuestion.objects.get(question=question)
        production = Production.objects.get(id=id)
        c['productionname'] =production.name
        c['pk']=question.competition_id
        c['url'] = production.file.url
        c['description']=production.description
        c['operation_instructions']=production.operation_instructions
        c['production_id'] = production.id
        c['limit_score'] = question.limit_score
        c['limit_small_score'] = question.limit_small_score
        name = Teacher.objects.get(username__exact=request.user).name
        c['name'] = name
    except Exception as e:
        return HttpResponseRedirect('/index/')
    if request.method == "POST":
        integrity_score = request.POST['integrity_score']
        technical_score = request.POST['technical_score']
        artistry_score = request.POST['artistry_score']
        creativity_score = request.POST['creativity_score']
        total_score = int(integrity_score) + int(technical_score) + int(artistry_score) + int(creativity_score)
        new_comment = request.POST['new_comment']
        small_score = {
            "创造性": creativity_score,
            "完整性": integrity_score,
            "艺术性": artistry_score,
            "技术性": technical_score,
        }
        if QuestionProductionScore.objects.filter(question=question,production=production,rater=Teacher.objects.get(username__exact=request.user)).exists():
            qss = QuestionProductionScore.objects.get(question=question,
                                                rater=Teacher.objects.get(username__exact=request.user),
                                                production=production, is_adviser=True)

            qss.small_score = small_score
            qss.score = int(total_score)
            qss.save()
            qsc = QuestionProductionScore.objects.get(question=question,
                                                rater=Teacher.objects.get(username__exact=request.user),
                                                production=production, is_adviser=True)
            qsc.comment = new_comment
            qsc.save()
        else:
            object = QuestionProductionScore(question=question, production=production,
                                             rater=Teacher.objects.get(username__exact=request.user),score=int(total_score), small_score=small_score ,comment=new_comment, is_adviser=True)

            object.save()

    if QuestionProductionScore.objects.filter(question=question,rater=Teacher.objects.get(username__exact=request.user),
                                              production= production).exists():
        teacher_score = QuestionProductionScore.objects.get(question=question,rater=Teacher.objects.get(username__exact=request.user),
                                                            production=production, is_adviser=True)
        c['teacher_score'] = teacher_score
    try:
        # print(id)
        # print(ANTLRScore.objects)
        antlr_score = ANTLRScore.objects.get(production_id=id)
        # print(antlr_score)
        score = model_to_dict(antlr_score, fields=['ap_score', 'parallelism_score', 'synchronization_score',
                                                   'flow_control_score', 'user_interactivity_score',
                                                   'logical_thinking_score', 'data_representation_score'])
        # print(score)
        score_dict = generate_dict_production(score)
        c['antlr_score'] = score_dict
        total_score = sum(score.values())
        c['total_score'] = total_score
        production_hints = ProductionHint.objects.filter(production_id=id)
        c['production_hints'] = production_hints
        name = Teacher.objects.get(username__exact=request.user).name
        c['name'] = name

        antlr_profile = Production_profile.objects.get(production_id=id)
        profile = model_to_dict(antlr_profile, fields=['motion_num', 'looklike_num', 'sounds_num',
                                                       'draw_num', 'event_num',
                                                       'control_num', 'sensor_num', 'operate_num', 'more_num',
                                                       'data_num', 'sprite_num', 'backdrop_num', 'snd_num'])
        c['profiles'] = profile
    except Exception as e:
        print(e)
        print("some error happen!")
    c.update(csrf(request))
    if not Teacher.objects.filter(username__exact=request.user).first().position:
        c['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
        if Position.objects.filter(name='普通教师'):
            Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
        else:
            p = Position.objects.create(name='普通教师',
                                        permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
            Teacher.objects.get(username__exact=request.user).position = p
    else:
        c['permissions'] = Teacher.objects.filter(username__exact=request.user).first().position.permissions
    return render(request, 'comprograde_adviser.html', c)


class CompetitionCreate(LoginRequiredMixin, CreateView):
    login_url = '/t/'
    success_url = '/t/competition_management_admin/'
    model = Competition
    template_name = "competition_management_new.html"
    fields = ['title', 'creator', 'rater', 'advisers',  'start_time', 'stop_time','content']

    def form_valid(self, form):
        # we need to add author field
        try:
            # we need to add lesson field
            return super(CompetitionCreate, self).form_valid(form)
        except Exception as e:
            print(e)
            return None


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context[
                'permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师',
                                            permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(
                username__exact=self.request.user).first().position.permissions
        return context


class CompetitionListAdviser(SingleTableView):
    model = Competition
    table_class = CompetitionAdviserTable
    template_name = "competition_management_adviser.html"

    # def get_queryset(self):
    #     user = self.request.user
    #     return Competition.objects.filter(advisers=user)
    #
    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #
    #     return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        user = self.request.user
        competition = Competition.objects.filter(advisers=user)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            competition = competition.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = CompetitionAdviserTable(competition)
            table.paginate(page=page, per_page=10)
            context['competition_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context[
                'permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师',
                                            permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(
                username__exact=self.request.user).first().position.permissions

        return context


class CompProAdviserList(SingleTableView):
    model = QuestionProductionScore
    table_class = ComProAdviserTable
    template_name = "compro_management_adviser.html"

    def get_queryset(self):
        user = self.request.user
        competition_id = self.kwargs.get("pk")
        comp = Competition.objects.get(id=competition_id)
        qs = QuestionProductionScore.objects.filter(question__in=CompetitionQuestion.objects.filter(competition=comp), is_adviser=False)\
            .values('production', 'question').annotate(avg_score=Avg('score'))

        data = [{'name': Production.objects.get(pk=item['production']).author,
                 'id': Production.objects.get(pk=item['production']).id,
                 'question': CompetitionQuestion.objects.get(pk=item['question']).question,
                 'production': Production.objects.get(pk=item['production']).name,
                 'create_time': Production.objects.get(pk=item['production']).create_time,
                 'ct_score': ANTLRScore.objects.get(
                     production_id=item['production']).total if ANTLRScore.objects.filter(
                     production_id=item['production']).exists() else None,
                 'avg_score': item['avg_score'],
                 'score': QuestionProductionScore.objects.get(question=item['question'], production=item['production'],
                                                              rater=user).score if QuestionProductionScore.objects.filter(
                     question=item['question'], production=item['production'], rater=user).exists() else None,
                 } for item in qs]
        # data.sort("id")
        return data

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # 排序
        sort = self.request.GET.get("sort", "")
        context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        competition_id = self.kwargs.get("pk")
        context['pk'] = competition_id
        context['raters'] = Competition.objects.get(id=competition_id).rater
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions

        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class GetComPro(SingleTableView):
    model = CompetitionQuestion
    table_class = ComProAdviserTable
    template_name = "compro_management_adviser.html"

    def get_queryset(self):
        target = self.request.GET.get('target', None)
        # print(target)
        user = self.request.user
        competition_id = self.kwargs.get("pk")
        print(competition_id)
        comp = Competition.objects.get(id=competition_id)
        qs = QuestionProductionScore.objects.filter(question__in=CompetitionQuestion.objects.filter(competition=comp),production=Production.objects.filter(id=target),
                                                    is_adviser=False) \
            .values('production', 'question').annotate(avg_score=Avg('score'))

        data = [{'name': Production.objects.get(pk=item['production']).author,
                 'id': Production.objects.get(pk=item['production']).id,
                 'question': CompetitionQuestion.objects.get(pk=item['question']).question,
                 'production': Production.objects.get(pk=item['production']).name,
                 'create_time': Production.objects.get(pk=item['production']).create_time,
                 'ct_score': ANTLRScore.objects.get(
                     production_id=item['production']).total if ANTLRScore.objects.filter(
                     production_id=item['production']).exists() else None,
                 'avg_score': item['avg_score'],
                 'score': QuestionProductionScore.objects.get(question=item['question'], production=item['production'],
                                                              rater=user).score if QuestionProductionScore.objects.filter(
                     question=item['question'], production=item['production'], rater=user).exists() else None,
                 } for item in qs]
        return data

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        competition_id = self.kwargs.get("pk")
        title_ = Competition.objects.get(id=competition_id).title
        context['pk']=competition_id
        context['title']=title_
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions
        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class CompProgressList(SingleTableView):
    model = QuestionProductionScore
    table_class = ComProgressTable
    template_name = "compro_progress.html"

    def get_queryset(self):
        user = self.request.user
        competition_id = self.kwargs.get("pk")
        print(competition_id)
        comp = Competition.objects.get(id=competition_id)
        qs = QuestionProductionScore.objects.filter(question__in=CompetitionQuestion.objects.filter(competition=comp), is_adviser=False)
        value_qs = qs.values('question__question', 'rater').annotate(
                         not_rated=Count(Case(When(score=None, then=1), output_field=IntegerField())),
                         total=Count('rater'),
                         avg_score=Avg('score'))

        data = [{'question': item['question__question'],
                 'rater': item['rater'],
                 'avg_score':  item['avg_score'],
                 'all_production': item['total'],
                 'score_production': item['not_rated'],
                } for item in value_qs]
        return data

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # 排序
        sort = self.request.GET.get("sort", "")
        context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        competition_id = self.kwargs.get("pk")
        context['pk'] = competition_id
        context['raters'] = Competition.objects.get(id=competition_id).rater
        print(Competition.objects.get(id=competition_id).rater)
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions

        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


class GetProgressList(SingleTableView):
    model = QuestionProductionScore
    table_class = ComProgressTable
    template_name = "compro_progress.html"

    def get_queryset(self):
        target = self.kwargs.get("target")
        # target = self.request.GET.get('target', None)
        user = self.request.user
        competition_id = self.kwargs.get("pk")
        print(competition_id)
        comp = Competition.objects.get(id=competition_id)
        qs = QuestionProductionScore.objects.filter(question__in=CompetitionQuestion.objects.filter(competition=comp),
                                                    is_adviser=False, rater=target)
        value_qs = qs.values('question__question', 'rater').annotate(
            not_rated=Count(Case(When(score=None, then=1), output_field=IntegerField())),
            total=Count('rater'),
            avg_score=Avg('score'))

        data = [{'question': item['question__question'],
                 'rater': item['rater'],
                 'avg_score': item['avg_score'],
                 'all_production': item['total'],
                 'score_production': item['not_rated'],
                 } for item in value_qs]
        return data

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # 排序
        sort = self.request.GET.get("sort", "")
        context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        competition_id = self.kwargs.get("pk")
        context['pk'] = competition_id
        context['raters'] = Competition.objects.get(id=competition_id).rater
        print(Competition.objects.get(id=competition_id).rater)
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions

        if not Teacher.objects.filter(username__exact=self.request.user).first().position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
        return context


# class ProblemList(SingleTableView):
#     model = Problem
#     table_class = ProblemTable
#     template_name = "problem_management.html"
#
#     def get_queryset(self):
#         user = self.request.user
#         return Problem.objects.filter(author=user)
#
#     def get_table(self, **kwargs):
#         table = super().get_table()
#         RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
#         return table
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context
#
#
# class GetProblem(SingleTableView):
#     model = Problem
#     table_class = ProblemTable
#     template_name = "problem_management.html"
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['title'] =Teacher.objects.get(username__exact=self.request.user).name
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context
#
#     def get_table(self, **kwargs):
#         table = super().get_table()
#         RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
#         return table
#
#     def get_queryset(self):
#         user = self.request.user
#         target = self.request.GET.get('target', None)
#         return Problem.objects.filter(author=user).filter(title=target)
#
#
# class ProblemCreate(LoginRequiredMixin, CreateView):
#     # if you want to custom or modify default form, change form_class parameter
#     #     form_class = ContactForm
#     login_url = '/t/'
#     success_url = '/t/problem_management/'
#     model = Problem
#     template_name = "problem_management_new.html"
#     fields = ['title','description','input_description','output_description','author','hint','accepted_number','permission','submission_number','time_limit','memory_limit']
#
#     def form_valid(self, form):
#         # we need to add author field
#         user = self.request.user
#         teacher = Teacher.objects.get(username=user)
#         form.instance.author = teacher
#         return super(ProblemCreate, self).form_valid(form)
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context
#
#
# class ProblemUpdate(ProblemAuthorRequiredMixin, UpdateView):
#     login_url = '/t/'
#     model = Problem
#     fields = ['title','description','input_description','output_description','hint','permission','author','time_limit','memory_limit','submission_number','accepted_number']
#     template_name = "problem_management_update.html"
#     success_url = '/t/problem_management/'
#
#     def get_object(self, queryset=None):
#         try:
#             problem_id = self.kwargs.get("problem")
#             return Problem.objects.get(id=problem_id)
#         except Exception as e:
#             return None
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context
#
#
# class ProblemDelete(DeleteView):
#     template_name = "problem_management_delete.html"
#     model = Problem
#     success_url = '/t/problem_management/'
#
#     def get_object(self, queryset=None):
#         try:
#             problem_id = self.kwargs.get("problem")
#             return Problem.objects.get(id=problem_id)
#         except Exception as e:
#             return None
#
#     def get_success_url(self):
#         return "/t/problem_management/"
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context
#
#
# class TestCasesList(SingleTableView):
#     model = TestCase
#     table_class = TestCasesTable
#     template_name = "test_cases_management.html"
#
#     def get_queryset(self):
#         problem_id = self.kwargs.get("problem")
#         problem1 = Problem.objects.filter(id=problem_id)
#         return TestCase.objects.filter(problem=problem1)
#
#     def get_table(self, **kwargs):
#         table = super().get_table()
#         RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
#         return table
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         context['id'] = self.kwargs.get("problem")
#         problem_id = self.kwargs.get("problem")
#         context['title'] = Problem.objects.get(id=problem_id).title
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context
#
#
# class GetTestCases(SingleTableView):
#     model = TestCase
#     table_class = TestCasesTable
#     template_name = "test_cases_management.html"
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         context['id'] = self.kwargs.get("problem")
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(username__exact=self.request.user).first().position.permissions
#         return context
#
#     def get_table(self, **kwargs):
#         table = super().get_table()
#         RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
#         return table
#
#     def get_queryset(self):
#         target = self.request.GET.get('target', None)
#         problem_id = self.kwargs.get("problem")
#         problem1 = Problem.objects.filter(id=problem_id)
#         if problem1:
#             return TestCase.objects.filter(problem=problem1).filter(name=target)
#
#
# class TestCasesCreate(ProblemAuthorRequiredMixin, CreateView):
#     login_url = '/t/'
#     model = TestCase
#     template_name = "test_cases_management_new.html"
#     fields = ['problem', 'input_test', 'output_test']
#     success_url = '/t/test_cases_management/'
#
#     def form_valid(self, form):
#         try:
#             # we need to add lesson field
#             problem1 = Problem.objects.get(id=self.kwargs.get("problem"))
#             # test_cases_id = TestCase.objects.filter(problem=problem1).count() + 1
#             form.instance.problem = problem1
#             # form.instance.chapter_id = test_cases_id
#             return super(TestCasesCreate, self).form_valid(form)
#         except Exception as e:
#             return None
#
#     def get_success_url(self):
#         return "/t/test_cases_management/" + self.kwargs.get("problem")
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         context['id'] = self.kwargs.get("problem")
#         problem_id = self.kwargs.get("problem")
#         context['title'] = Problem.objects.get(id=problem_id).title
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context[
#                 'permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师',
#                                             permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(
#                 username__exact=self.request.user).first().position.permissions
#         return context
#
#
# class TestCasesUpdate(ProblemAuthorRequiredMixin, UpdateView):
#     login_url = '/t/'
#     model = TestCase
#     fields = ['problem', 'input_test', 'output_test']
#     template_name = "test_cases_management_update.html"
#
#     def get_object(self, queryset=None):
#         try:
#             problem_id = self.kwargs.get("problem")
#             problem1 = Problem.objects.filter(id=problem_id)
#             if problem1:
#                 test_cases = self.kwargs.get("test_cases")
#
#                 return TestCase.objects.get(problem=problem1, order=test_cases)
#         except Exception as e:
#             return None
#
#     def get_success_url(self):
#         return "/t/test_cases_management/" + self.kwargs.get("problem")
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         context['id'] = self.kwargs.get("problem")
#         problem_id = self.kwargs.get("problem")
#         context['title'] = Problem.objects.get(id=problem_id).title
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context[
#                 'permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师',
#                                             permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(
#                 username__exact=self.request.user).first().position.permissions
#         return context
#
#
# class TestCasesDelete(DeleteView):
#     template_name = "test_cases_management_delete.html"
#     model = TestCase
#
#     def get_object(self, queryset=None):
#         try:
#             problem_id = self.kwargs.get("problem")
#             problem1 = Problem.objects.filter(id=problem_id)
#             if problem1:
#                 test_cases = self.kwargs.get("test_cases")
#
#                 return TestCase.objects.get(problem=problem1, order=test_cases)
#         except Exception as e:
#             return None
#
#     def get_success_url(self):
#         return "/t/test_cases_management/" + self.kwargs.get("problem")
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the context
#         context['name'] = Teacher.objects.get(username__exact=self.request.user).name
#         context['id'] = self.kwargs.get("problem")
#         problem_id = self.kwargs.get("problem")
#         context['title'] = Problem.objects.get(id=problem_id).title
#         if not Teacher.objects.filter(username__exact=self.request.user).first().position:
#             context[
#                 'permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
#             if Position.objects.filter(name='普通教师'):
#                 Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
#             else:
#                 p = Position.objects.create(name='普通教师',
#                                             permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
#                 Teacher.objects.get(username__exact=self.request.user).position = p
#         else:
#             context['permissions'] = Teacher.objects.filter(
#                 username__exact=self.request.user).first().position.permissions
#         return context

# ---------------------BELOWS ARE API FOR AJAX -----------------------------------------------------------

def ajax_school(request):
    teacher = Teacher.objects.get(username__exact=request.user)
    class_ = Class.objects.filter(teacher=teacher)
    schools = class_.values('school_name').distinct()
    school_name = School.objects.filter(school_name__in=schools)
    result = json.dumps(school_name)
    return HttpResponse(result, content_type='application/json')

def resetpwd(request):
    if request.method == 'POST':
        ret = {'status': 1001}
        usernames = request.POST.get('username')
        try:
            for username in usernames:
                stu = User.objects.get(username=username)
                stu.set_password('123456')
                stu.save()
        except Exception as e:
            ret = {'status': 1001}
        ret['status'] = 1002
        teacher = Teacher.objects.get(username__exact=request.user)
        notify.send(sender=teacher, recipient=teacher, actor=teacher, verb='批量修改密码成功', description='学生密码已修改为123456')
        return HttpResponse(json.dumps(ret))
    return render(request, 'student_management.html')
# def ajax_class(request):
#     school = request.GET.get('school')
#     teacher = Teacher.objects.get(username__exact=request.user)
#     class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)
#     response = serializers.serialize("json", class_)
#     return HttpResponse(response, content_type='application/json')


def competition_sign(request):
    if request.method == 'POST':
        ret = {'status': 1000}
        usernames = request.POST.get('username')
        usernames1 = json.loads(usernames)
        competition_title = request.POST.get('competition_title')
        teacher = Teacher.objects.get(username__exact=request.user)
        if len(usernames1):
            pass
        else:
            ret = {'status': 1005}
        try:
            for username in usernames1:
                if Competition.objects.filter(title=competition_title).exists():
                    competition1 = Competition.objects.get(title=competition_title)
                    # competition1.save()
                    if User.objects.filter(username=username).exists():
                        user1 = User.objects.get(username=username)
                        # user1.save()
                        teacher1 = Teacher.objects.get(name=teacher)
                        if CompetitionUser.objects.filter(competition=competition1, user=user1, tutor=teacher1).exists():
                            ret = {'status': 1004}
                        else:
                            competition_user = CompetitionUser(competition=competition1, user=user1, tutor=teacher1)
                            competition_user.save()
                            ret['status'] = 1002
                else:
                    ret = {'status': 1003}
        except Exception as e:
            ret = {'status': 1001}
        return HttpResponse(json.dumps(ret))
    return render(request, 'student_management.html')

def ajax_class(request):
    school = request.GET.get('school')
    teacher = Teacher.objects.filter(username__exact=request.user)
    if teacher:
        teacher = teacher.first()
    else:
        return HttpResponse("[]", content_type='application/json')
    class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)
    if class_:
        response = serializers.serialize("json", class_)
        # print(response)
        return HttpResponse(response, content_type='application/json')
    else:
        return HttpResponse("[]", content_type='application/json')


def ajax_student(request):
    class_ = request.GET.get('class')
    if not class_:
        return HttpResponse("[]", content_type='application/json')
    class_ = Class.objects.get(pk=class_)
    student = User.objects.filter(classes__exact=class_)
    if student:
        response = serializers.serialize("json", student)
        # print(response)
        return HttpResponse(response, content_type='application/json')
    else:
        return HttpResponse("[]", content_type='application/json')


def ajax_production(request):
    name = request.GET.get('name')
    student = request.GET.get('student')
    class_ = request.GET.get('class')
    school = request.GET.get('school')
    if student:
        production = Production.objects.filter(author__exact=student).filter(is_active = True)
    elif class_:
        class_ = Class.objects.get(pk=class_)
        # student = User.objects.filter(classes__in=class_)
        student = User.objects.filter(classes__exact=class_)
        production = Production.objects.filter(author__in=student).filter(is_active = True)
    else:
        teacher = Teacher.objects.get(username__exact=request.user)
        class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)

        # student = User.objects.filter(classes__in=class_)
        student = User.objects.filter(classes__in=class_)
        production = Production.objects.filter(author__in=student).filter(is_active = True)
    if name:
        production = production.filter(name__contains=name).filter(is_active = True)
    response = serializers.serialize("json", production)
    return HttpResponse(response, content_type='application/json')


def get_teachers_score_and_comment_of_productions_by_ids(request):
    array = request.POST.getlist('ids')
    # score = []
    # comment = []
    result = []
    for i in array:
        result.append({})
        if TeacherScore.objects.filter(production_id=i).exists():
            # score.append(TeacherScore.objects.get(production_id=i).score)
            # comment.append(TeacherScore.objects.get(production_id=i).comment)
            result[-1]["score"] = TeacherScore.objects.get(production_id=i).score
            result[-1]["comment"] = TeacherScore.objects.get(production_id=i).comment
        else:
            result[-1]["score"] = "暂时还没有评分！"
            result[-1]["comment"] = "暂时还没有评价"
    # result = {}
    # result["score"] = score
    # result["comment"] = comment
    # print(result)
    #json.dumps(result)
    #result = serializers.serialize("json", result)
    return HttpResponse(json.dumps(result, ensure_ascii=False, indent=2), content_type='application/json')


# ---------------------END OF API FOR AJAX -----------------------------------------------------------

class GetTeacherTable(SingleTableView):
    model = Teacher
    table_class = TeacherTable
    template_name = "permission_manage.html"

    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table
    #
    # def get_queryset(self):
    #     return Teacher.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        teacher = Teacher.objects.all()
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            teacher = teacher.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = TeacherTable(teacher)
            table.paginate(page=page, per_page=10)
            context['teacher_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions
        if not Teacher.objects.get(username__exact=self.request.user).position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.get(username__exact=self.request.user).position.permissions
        return context


class GetTeacher(SingleTableView):
    model = Teacher
    table_class = TeacherTable
    template_name = "permission_manage.html"

    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table
    #
    # def get_queryset(self):
    #     teacher_name = self.request.GET.get("target", None)
    #     teacher = Teacher.objects.filter(name=teacher_name)
    #     return teacher

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # teacher_name = self.request.GET.get("target", None)
        teacher_name = self.kwargs.get("target")
        teacher = Teacher.objects.filter(name=teacher_name)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            teacher = teacher.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = TeacherTable(teacher)
            table.paginate(page=page, per_page=10)
            context['teacher_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        # context['permissions'] = Teacher.objects.get(username__exact=self.request.user).permissions
        if not Teacher.objects.get(username__exact=self.request.user).position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.get(username__exact=self.request.user).position.permissions
        return context


# class AllPermissions(ListView):
#     template_name = "allpositions.html"
#     context_object_name = "positions"
#
#     def get_queryset(self):
#         positions = Position.objects.all()
#         return positions


class AllPermissions(ListView):
    template_name = "allpositions.html"
    context_object_name = "positions"

    def get_queryset(self):
        positions = Position.objects.all()
        return positions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not Teacher.objects.get(username__exact=self.request.user).position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.get(username__exact=self.request.user).position.permissions
        if Teacher.objects.get(username__exact=self.request.GET.get('user')).position:
            context['position'] = Teacher.objects.get(username__exact=self.request.GET.get('user')).position.name
        else:
            context['position'] = '普通教师'
        return context

class AddPositions(ListView):
    template_name = "allpermissions.html"

    def get_queryset(self):
        positions = Position.objects.all()
        return positions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not Teacher.objects.get(username__exact=self.request.user).position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.get(username__exact=self.request.user).position.permissions
        return context


class CheckPositions(ListView):
    template_name = "checkpositions.html"
    context_object_name = "positions"

    def get_queryset(self):
        positions = Position.objects.all()
        return positions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not Teacher.objects.get(username__exact=self.request.user).position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.get(username__exact=self.request.user).position.permissions
        return context


class CheckOnePositions(ListView):
    template_name = "check_one_position.html"

    def get_queryset(self):
        position = self.request.GET.get("position")
        position = Position.objects.get(name=position)
        return position

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not Teacher.objects.get(username__exact=self.request.user).position:
            context['permissions'] = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage"
            if Position.objects.filter(name='普通教师'):
                Teacher.objects.get(username__exact=self.request.user).position = Position.objects.get(name='普通教师')
            else:
                p = Position.objects.create(name='普通教师', permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")
                Teacher.objects.get(username__exact=self.request.user).position = p
        else:
            context['permissions'] = Teacher.objects.get(username__exact=self.request.user).position.permissions
        position = self.request.GET.get("position")
        context['position'] = Position.objects.get(name=position).permissions
        # print(context['position'])
        return context


class ChangeTeacherPermission(APIView):

    def post(self, request):
        user = self.request.GET.get('user', None)
        user = Teacher.objects.get(username=user)
        position = self.request.GET.get('position', None)
        # print(position)
        position = Position.objects.get(name=position)
        user.position = position
        user.save()
        return HttpResponse("ok")


class AddTeacherPermission(APIView):

    def post(self, request):
        permissions = json.loads(self.request.POST.get('obj'))['permissions']
        name = json.loads(self.request.POST.get('obj'))['name']
        permissions = ','.join(permissions)
        position = Position.objects.create(name=name, permissions=permissions)
        position.save()
        return HttpResponse("ok")
