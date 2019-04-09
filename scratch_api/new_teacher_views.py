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
from django.contrib.auth.hashers import make_password
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
from scratch_api.tables import ProdcutionTable, ProdcutionGradeTable, ProdcutionDownloadTable, ClassTable, UserTable, \
    CourseTable, ChapterTable, ProblemTable, TestCasesTable, ApplyTable
from scratch_api.mixins import CourseAuthorRequiredMixin,CompetitionAuthorRequiredMixin
from scratch_api.tables import ProdcutionTable, ProdcutionGradeTable, ProdcutionDownloadTable, ClassTable, UserTable, \
    CourseTable, ChapterTable, TeacherTable, CompetitionTable, ComProTable, CompetitionAdminTable, ComProAdminTable,CompetitionAdviserTable, \
    UserListTable,ComUserTable,ComProAdviserTable,ComProgressTable,ComProScoreTable, ClassAddUserTable
# from scratch_api.tasks import import_student_excel
# from util.excel import import_student_excel
from website.mixins import IsLoginMixin, AuthorRequiredMixin
from .models import Class, Teacher, School, User, Production, TeacherScore, CommentEachOther, ANTLRScore, CompetitionUser, \
    ProductionHint, Production_profile, Position, Competition, CompetitionQuestion, QuestionProductionScore, Adviser, FormatSchool, FormatClass
from .forms import MyAuthenticationForm, SignUpForm, UserUpdateForm, TeacherSettingForm, TeacherChangePasswordForm
from gen.Gen import gen
from .tasks import import_student_excel, import_competition_user_excel, import_teacher_excel, upload_QuesProScore, \
    import_school_excel, import_user_excel,import_class_excel
from OJ.models import Problem, TestCase
from django.apps import apps
from guardian.shortcuts import remove_perm, assign_perm
from django.db.models import Q, Avg, Count, F, Case, When, FloatField, IntegerField


# 单个注册学校
@login_required(login_url='/')
def import_school(request):
    c = {}
    if request.method == 'POST':
        ret = {'status': 1000}
        province = request.POST.get("province", None)
        city = request.POST.get("city", None)
        country = request.POST.get("country", None)
        school = request.POST.get("school", None)
        chief = request.POST.get("chief", None)
        print(chief)
        chief_ = Teacher.objects.get(username=chief)
        if Teacher.objects.filter(username=chief).exists():
            if FormatSchool.objects.filter(province=province, city=city, district=country, name=school).exists():
                if not FormatSchool.objects.filter(province=province, city=city, district=country, name=school).first().is_active:
                    # 1004: 代表学校已经存在，但未激活
                    ret = {'status': 1004}
                else:
                    ret = {'status': 1001}
            else:
                fschool = FormatSchool(province=province, city=city, district=country, name=school, chief=chief_)
                fschool.save()
                notify.send(sender=chief_, recipient=chief_, actor=chief_, verb="新建学校审核中",
                            description="您申请新建的学校：" + fschool.__str__() + ",正在审核中，请联系教研员或管理员通过审核")
                try:
                    # 给教研员发申请信息
                    advisers = Adviser.objects.filter(local_province=province, local_city=city, local_district=country)
                    for adviser in advisers:
                        notify.send(sender=chief_, recipient=adviser, actor=chief_, verb="请求新建学校",
                                    target=fschool,
                                    description=chief_.name + "(" + chief_.username + ")请求新建学校："
                                                + fschool.__str__() + ", 快去审核吧！")
                except:
                    pass
                ret = {'status': 1002}

        else:
            ret = {'status': 1003}
            # c.update(csrf(request))
            # return render(request, "import_school.html", c)
        return HttpResponse(json.dumps(ret))
    else:
        c['teachers'] = Teacher.objects.all()
        c.update(csrf(request))
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
        return render(request, "import_school.html", c)


# 批量注册学校
@login_required(login_url='/t/')
def import_school_all(request):
    c = {}
    if request.method == "POST":
        upload_file = request.FILES.get("myfile", None)
        province = request.POST.get("province", None)
        city = request.POST.get("city", None)
        country = request.POST.get("country", None)
        if not upload_file:
            return HttpResponse("no files for upload!")
        else:
            file = upload_file.read()
            c['name'] = Teacher.objects.get(username__exact=request.user).name
            teacher = Teacher.objects.get(username__exact=request.user)
            import_school_excel.delay(file, teacher, province, city, country)
            c.update(csrf(request))
            return render(request, "import_school.html", c)
    else:
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
        return render(request, "import_school.html", c)


# 批量注册学生
@login_required(login_url='/t/')
def import_user(request):
    c = {}
    teacher = Teacher.objects.get(username__exact=request.user)
    position = teacher.position
    c['position'] = position
    c['teacher'] = teacher.name
    if teacher.format_school:
        school = teacher.format_school
        fschool = FormatSchool.objects.get(name=school)
        school_chief = fschool.chief.username
        if school_chief == teacher.username:
            c["is_chief"] = "true"
        else:
            c['is_chief'] = "false"
            c['chief_username'] = teacher.username
            c['chief_name'] = teacher.name
        province = fschool.province
        city = fschool.city
        country = fschool.district
        c['province'] = province
        c['city'] = city
        c['country'] = country
        c['school'] = fschool.name
        c['is_school'] = "true"
    else:
        c['is_school'] = "false"
    if request.method == "POST":
        province = request.POST.get("province", None)
        city = request.POST.get("city", None)
        country = request.POST.get("country", None)
        school = request.POST.get("school", None)
        class_ = request.POST.get("class", None)
        upload_file = request.FILES.get("myfile", None)
        if not upload_file:
            return HttpResponse("no files for upload!")
        else:
            file = upload_file.read()
            c['name'] = Teacher.objects.get(username__exact=request.user).name
            teacher = Teacher.objects.get(username__exact=request.user)
            import_user_excel.delay(file, teacher, province, city, country, school, class_)
            c.update(csrf(request))
            return render(request, "import_school.html", c)
    else:
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

        c.update(csrf(request))
        return render(request, "import_user.html", c)


# 下拉框通过【省市区】获取学校
@login_required(login_url='/t/')
def import_user_school(request):
    c = {}
    if request.method == "POST":
        province = request.POST.get("province", None)
        city = request.POST.get("city", None)
        country = request.POST.get("country", None)
        school_list = []
        for i in FormatSchool.objects.filter(province=province, city=city, district=country):
            school_list.append(i.name)
        c.update(csrf(request))
        return HttpResponse(json.dumps(school_list))
        return render(request, "import_user.html", "import_class.html", c)
    else:
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

        c.update(csrf(request))
        return render(request, "import_user.html", c)


# 下拉框通过【省市区学校】获取班级
@login_required(login_url='/t/')
def import_user_class(request):
    c = {}
    if request.method == "POST":
        province = request.POST.get("province", None)
        city = request.POST.get("city", None)
        country = request.POST.get("country", None)
        school = request.POST.get("school", None)
        school_ = FormatSchool.objects.get(province=province, city=city, district=country, name=school)
        class_list = []
        for i in FormatClass.objects.filter(format_school=school_):
            arg = {}
            arg['name'] = i.get_full_name()
            arg['id'] = i.pk
            arg['is_interest'] = i.is_interest
            class_list.append(arg)
        c.update(csrf(request))
        return HttpResponse(json.dumps(class_list), content_type="application/json")
    else:
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

        c.update(csrf(request))
        return render(request, "import_user.html", c)


@login_required(login_url='/t/')
def import_user_class_nadmin(request):
    c = {}
    if request.method == "POST":
        province = request.POST.get("province", None)
        city = request.POST.get("city", None)
        country = request.POST.get("country", None)
        school = request.POST.get("school", None)
        school_ = FormatSchool.objects.get(province=province, city=city, district=country, name=school)
        teacher = Teacher.objects.get(username__exact=request.user)
        class_list = []
        for i in FormatClass.objects.filter(format_school=school_, chief=teacher):
            arg = {}
            arg['name'] = i.get_full_name()
            arg['id'] = i.pk
            arg['is_interest'] = i.is_interest
            class_list.append(arg)
        c.update(csrf(request))
        return HttpResponse(json.dumps(class_list), content_type="application/json")
    else:
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

        c.update(csrf(request))
        return render(request, "import_user.html", c)


# 下拉框通过【学校，负责人，是否为兴趣班】获取班级
@login_required(login_url='/t/')
def import_school_class(request):
    c = {}
    teacher = Teacher.objects.get(username__exact=request.user)
    if request.method == "POST":
        school = request.POST.get("school", None)
        school_ = FormatSchool.objects.get(id=school)
        print(school_)
        class_list = []
        for i in FormatClass.objects.filter(format_school=school_, chief=teacher):
            arg = {}
            arg['name'] = i.get_full_name()
            arg['id'] = i.pk
            arg['is_interest'] = i.is_interest
            class_list.append(arg)
        print(class_list)
        c.update(csrf(request))
        return HttpResponse(json.dumps(class_list), content_type="application/json")
        return render(request, "new_class_management.html", c)
    else:
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

        c.update(csrf(request))
        return render(request, "new_class_management.html", c)


# 下拉框通过【学校】获取班级
@login_required(login_url='/t/')
def get_all_class(request):
    c = {}
    if request.method == "POST":
        school = request.POST.get("school", None)
        print(school)
        school_ = FormatSchool.objects.get(id=school)
        class_list = []
        for i in FormatClass.objects.filter(format_school=school_):
            arg = {}
            arg['name'] = i.get_full_name()
            arg['id'] = i.pk
            arg['is_interest'] = i.is_interest
            class_list.append(arg)
        c.update(csrf(request))
        return HttpResponse(json.dumps(class_list), content_type="application/json")
    else:
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

        c.update(csrf(request))
        return render(request, "student_list.html", c)


# 下拉框通过【省市区，学校】获取教师
@login_required(login_url='/t/')
def import_class_teacher(request):
    c = {}
    if request.method == "POST":
        province = request.POST.get("province", None)
        city = request.POST.get("city", None)
        country = request.POST.get("country", None)
        school = request.POST.get("school", None)
        school_ = FormatSchool.objects.get(province=province, city=city, district=country, name=school)
        teachers = Teacher.objects.filter(format_school=school_)
        teachers_list = []
        for i in teachers:
            arg = {}
            arg['name'] = i.name
            arg['username'] = i.username
            teachers_list.append(arg)
        c.update(csrf(request))
        return HttpResponse(json.dumps(teachers_list), content_type="application/json")
        return render(request, "import_class.html", c)
    else:
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

        c.update(csrf(request))
        return render(request, "import_class.html", c)


# 单个注册班级
@login_required(login_url='/t/')
def import_class(request):
    c = {}
    ret = {'status': 1000}
    teacher = Teacher.objects.get(username__exact=request.user)
    position = teacher.position
    c['position'] = position
    c['teacher'] = teacher.name
    if teacher.format_school:
        school = teacher.format_school
        fschool = FormatSchool.objects.get(name=school)
        school_chief = fschool.chief.username
        if school_chief == teacher.username:
            c["is_chief"] = "true"
        else:
            c['is_chief'] = "false"
            c['chief_username'] = teacher.username
            c['chief_name'] = teacher.name
        province = fschool.province
        city = fschool.city
        country = fschool.district
        c['province'] = province
        c['city'] = city
        c['country'] = country
        c['school'] = fschool.name
        c['is_school'] = "true"
    else:
        c['is_school'] = "false"
    if request.method == "POST":
        province = request.POST.get("province", None)
        city = request.POST.get("city", None)
        country = request.POST.get("country", None)
        school = request.POST.get("school", None)
        grade = request.POST.get("grade", None)
        class_num = request.POST.get("class_num", None)
        chief = request.POST.get("chief", None)
        is_interest = request.POST.get("is_interest", None)
        if is_interest == "true":
            is_ = True
        else:
            is_ = False
        teacher = Teacher.objects.get(username=chief)
        school_ = FormatSchool.objects.get(province=province, city=city, district=country, name=school)
        if Teacher.objects.filter(username=chief).exists():
            if FormatClass.objects.filter(format_school=school_, grade=grade, class_num=class_num,
                                          is_interest=is_).exists():
                if not FormatClass.objects.filter(format_school=school_, grade=grade, class_num=class_num,
                                          is_interest=is_).first().is_active:
                    # 1004: 代表班级已存在但是未激活
                    ret = {'status': 1004}
                else:
                    # 1001: 代表班级已存在且已激活
                    ret = {'status': 1001}
            else:
                format_class = FormatClass(format_school=school_, grade=grade, class_num=class_num,
                                           is_interest=is_, chief=teacher)
                format_class.save()
                notify.send(sender=teacher, recipient=teacher, actor=teacher, verb="新建班级审核中",
                            description="您申请新建的班级：" + format_class.__str__() + ",正在审核中，请联系学校负责人。")
                # 给学校负责人发送申请消息
                notify.send(sender=teacher, recipient=school_.chief, actor=teacher, verb="请求新建班级",
                            target=format_class,
                            description=teacher.name + "(" + teacher.username + ")请求新建班级："
                                        + format_class.get_full_name() + "，快去审核吧！")
                # 给管理员发送申请消息


                ret = {'status': 1002}
        else:
            ret = {'status': 1003}
        c.update(csrf(request))
        return HttpResponse(json.dumps(ret))
        # return render(request, "import_class.html", c)
    else:
        # 判断是否为老师
        try:
            # 关联（ select_realated ）position获取教师，只执行一次查库操作
            teacher = Teacher.objects.select_related("position").get(username__exact=request.user)
        except Exception as e:
            c['no_access'] = "您不是老师，无权访问！"
            c['render_url'] = "/"
            return render(request, 'import_class.html', c)

        c['name'] = teacher.name
        if not teacher.position:
            try:
                general_position = Position.objects.get(name="普通教师")
            except Exception:
                general_position = Position.objects.create(name="普通教师",
                                                           permission=Position.GENERAL_PERMISSION)
            teacher.position = general_position
            teacher.save()
        c['permissions'] = teacher.position.permissions
        # 判断权限中是否有新建班级的权限
        # if not 'download_production' in teacher.position.permissions:
        #     c["no_access"] = "您没有权限查看该版块！"
        #     c['render_url'] = '/t/index'
        #     return render(request, 'import_class.html', c)
        c.update(csrf(request))
        return render(request, "import_class.html", c)


# 批量注册教师
@login_required(login_url='/t/')
def new_import_teacher(request):
    c = {}
    if request.method == "POST":
        province = request.POST.get("province", None)
        city = request.POST.get("city", None)
        country = request.POST.get("country", None)
        school = request.POST.get("school", None)
        upload_file = request.FILES.get("myfile", None)
        if not upload_file:
            return HttpResponse("no files for upload!")
        else:
            file = upload_file.read()
            c['name'] = Teacher.objects.get(username__exact=request.user).name
            teacher = Teacher.objects.get(username__exact=request.user)
            import_teacher_excel.delay(file, teacher, province, city, country, school)
            c.update(csrf(request))
            return render(request, "new_import_teacher.html", c)
    else:
        c['name'] = Teacher.objects.get(username__exact=request.user).name

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

        c.update(csrf(request))
        return render(request, "new_import_teacher.html", c)


# 下拉框通过【负责人】获取学校
@login_required(login_url='/t/')
def format_class_management(request):
    c = {}
    if request.method == "POST":
        get_school = request.POST.get("get_school", None)
        teacher = Teacher.objects.get(username__exact=request.user)
        fschool = teacher.format_school
        # class_ = FormatClass.objects.filter(chief=teacher)
        # class_.values('format_school').distinct()
        print(fschool)
        # fschool = FormatSchool.objects.filter()
        print(teacher)
        fschools = FormatSchool.objects.filter(name=fschool)
        print(fschools)
        school_list = []
        for i in fschools:
            arg = {}
            arg['name'] = i.name
            arg['id'] = i.id
            arg['province'] = i.province
            arg['city'] = i.city
            arg['district'] = i.district
            school_list.append(arg)
        c.update(csrf(request))
        return HttpResponse(json.dumps(school_list))
        # return render(request, "new_class_management.html", c)
    else:
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

        c.update(csrf(request))
        return render(request, "new_class_management.html", c)


# 下拉框获取所有学校
@login_required(login_url='/t/')
def get_all_school(request):
    c = {}
    if request.method == "POST":
        get_school = request.POST.get("get_school", None)
        fschools = FormatSchool.objects.all()
        print(fschools)
        school_list = []
        for i in fschools:
            arg = {}
            arg['name'] = i.name
            arg['id'] = i.id
            arg['province'] = i.province
            arg['city'] = i.city
            arg['district'] = i.district
            school_list.append(arg)
        c.update(csrf(request))
        return HttpResponse(json.dumps(school_list))
        # return render(request, "new_class_management.html", c)
    else:
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

        c.update(csrf(request))
        return render(request, "new_class_management.html", c)


# 搜索通过【选择学校，班级】获取班级列表
class GetClass(SingleTableView):
    model = FormatClass
    table_class = ClassTable
    template_name = "new_class_management.html"

    # def get_queryset(self):
    #     class_ = self.request.GET.get('class', None)
    #     print(class_)
    #     teacher = self.request.user
    #     is_interest = FormatClass.objects.get(id=class_).is_interest
    #     return FormatClass.objects.filter(chief=teacher, id=class_, is_interest=is_interest)
    #
    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        class_ = self.kwargs.get("target")
        # class_ = self.request.GET.get('class', None)
        teacher = self.request.user
        is_interest = FormatClass.objects.get(id=class_).is_interest
        fclass = FormatClass.objects.filter(chief=teacher, id=class_, is_interest=is_interest)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            fclass = fclass.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = ClassTable(fclass)
            table.paginate(page=page, per_page=10)
            context['class_table'] = table
        except Exception as e:
            pass
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


# 搜索通过【选择学校】获取班级列表
class GetAllStudent(SingleTableView):
    model = User
    table_class = UserListTable
    template_name = "student_list.html"

    # def get_queryset(self):
    #     # teacher = self.request.user
    #     class_ = self.request.GET.get("class", None)
    #     student = User.objects.filter(format_class=class_)
    #     return student
    #
    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        class_ = self.kwargs.get("target")
        # class_ = self.request.GET.get("class", None)
        student = User.objects.filter(format_class=class_)
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


# 班级管理列表
class ClassManagementList(IsLoginMixin, SingleTableView):
    model = FormatClass
    table_class = ClassTable
    template_name = "new_class_management.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # 判断是否为老师
        try:
            # 关联（ select_realated ）position获取教师，只执行一次查库操作
            teacher = Teacher.objects.select_related("position").get(username__exact=self.request.user)
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
        # 判断权限中是否有查看作品列表的权限
        if not 'batch_signup' in teacher.position.permissions:
            context["no_access"] = "您没有权限查看该版块！"
            context['render_url'] = '/t/index'
            return context

        fclass = FormatClass.objects.filter(chief=teacher)
        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            fclass = fclass.order_by(sort)
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page
        try:
            table = ClassTable(fclass)
            table.paginate(page=page, per_page=10)
            context['class_table'] = table
        except Exception as e:
            pass
        return context


# 班级删除
class ClassDelete(DeleteView):
    template_name = "class_management_delete.html"
    model = FormatClass
    success_url = '/t/class_management/'

    def get_object(self, queryset=None):
        try:
            class_id = self.kwargs.get("class")
            return FormatClass.objects.get(pk=class_id)
        except Exception as e:
            return None

    def get_success_url(self):
        return "/t/class_management/"

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


# 班级学生列表
class ClassManagementAdd(SingleTableView):
    model = User
    table_class = ClassAddUserTable
    template_name = "class_management_add.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # teacher = self.request.user
        # class_id = self.kwargs.get("class_id")
        # class_ = FormatClass.objects.filter(chief=teacher, id=class_id)
        # school = FormatSchool.objects.filter(formatclass=class_)
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
            table = ClassAddUserTable(student)
            table.paginate(page=page, per_page=10)
            context['student_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        context['class_name'] = FormatClass.objects.get(id=self.kwargs.get("class_id")).get_full_name()
        context['class_id'] = self.kwargs.get("class_id")
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


# 搜索通过【学生真实姓名】获取学生列表
class GetAddStudent(SingleTableView):
    model = User
    table_class = ClassAddUserTable
    template_name = "class_management_add.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        target = self.kwargs.get("target")
        student = User.objects.filter(name=target)
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
            table = ClassAddUserTable(student)
            table.paginate(page=page, per_page=10)
            context['student_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['class_name'] = Class.objects.get(id=self.kwargs.get("class_id")).class_name
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        context['class_id'] = self.kwargs.get("class_id")
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


# 班级学生列表
class StudentManagementList(SingleTableView):
    model = FormatClass
    table_class = UserTable
    template_name = "student_management.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        teacher = self.request.user
        class_id = self.kwargs.get("class_id")
        class_ = FormatClass.objects.filter(chief=teacher, id=class_id)
        if class_:
            student = User.objects.filter(format_class=class_)
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
            table = UserTable(student)
            table.paginate(page=page, per_page=10)
            context['student_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        context['class_name'] = FormatClass.objects.get(id=self.kwargs.get("class_id")).get_full_name()
        context['class_id'] = self.kwargs.get("class_id")
        # context['class_name'] = Class.objects.get(id=self.kwargs.get("class_id")).class_name
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
    #     teacher = self.request.user
    #     class_id = self.kwargs.get("class_id")
    #     class_ = FormatClass.objects.filter(chief=teacher, id=class_id)
    #     if class_:
    #         student = User.objects.filter(format_class=class_)
    #     return student


# 学生信息更新
class StudentManagementUpdate(UpdateView):
    model = User
    template_name = "student_management_update.html"
    success_url = '/t/class_management/'
    form_class = UserUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add in the context
        # print(self.request.user)
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        # context['class_name'] = FormatClass.objects.get(id=self.kwargs.get("class_id")).get_full_name()
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

    def get_success_url(self, **kwargs):
        class_id = self.kwargs.get("class_id")
        return '/t/class_management/' + class_id + '/'


# 学生信息更新
class AllStudentManagementUpdate(UpdateView):
    model = User
    template_name = "all_student_management_update.html"
    success_url = '/t/student_list/'
    form_class = UserUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add in the context
        # print(self.request.user)
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        # context['class_name'] = FormatClass.objects.get(id=self.kwargs.get("class_id")).get_full_name()
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


# 搜索通过【学生真实姓名】获取学生列表
class GetStudent(SingleTableView):
    model = FormatClass
    table_class = UserTable
    template_name = "student_management.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        class_ = FormatClass.objects.filter(id=self.kwargs.get("class_id"), chief=self.request.user)
        if class_:
            target = self.kwargs.get("target")
            student = User.objects.filter(name=target, format_class__in=class_)
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
            table = UserTable(student)
            table.paginate(page=page, per_page=10)
            context['student_table'] = table
        except Exception as e:
            pass
        # Add in the context
        context['class_name'] = Class.objects.get(id=self.kwargs.get("class_id")).class_name
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

    # def get_table(self, **kwargs):
    #     table = super().get_table()
    #     RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
    #     return table
    #
    # def get_queryset(self):
    #     class_ = FormatClass.objects.filter(id=self.kwargs.get("class_id"), chief=self.request.user)
    #     if class_:
    #         target = self.kwargs.get("target")
    #         student = User.objects.filter(name=target, format_class__in=class_)
    #         return student
    #     pass


# 搜索通过【学生真实姓名】获取学生列表
class GetStudentSou(SingleTableView):
    model = FormatClass
    table_class = UserListTable
    template_name = "student_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        target = self.kwargs.get("target")
        context['target'] = target
        student = User.objects.filter(name=target)
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
    #     target = self.kwargs.get("target")
    #     student = User.objects.filter(name=target)
    #     return student


@login_required(login_url="/")
def blank(request):
    c = {}
    # 判断是否为老师
    try:
        # 关联（ select_realated ）position获取教师，只执行一次查库操作
        teacher = Teacher.objects.select_related("position").get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        c['render_url'] = "/"
        return render(request, 'blank.html', c)

    c['name'] = teacher.name
    if not teacher.position:
        try:
            general_position = Position.objects.get(name="普通教师")
        except Exception:
            general_position = Position.objects.create(name="普通教师",
                                                       permission=Position.GENERAL_PERMISSION)
        teacher.position = general_position
        teacher.save()
    c['permissions'] = teacher.position.permissions
    # 判断权限中是否有查看作品列表的权限
    if not ('analysis_production' in teacher.position.permissions or 'analysis_class' in teacher.position.permissions):
        c["no_access"] = "您没有权限查看该版块！"
        c['render_url'] = '/t/index'
    return render(request, 'blank.html', c)


def class_add_stu(request):
    if request.method == 'POST':
        ret = {'status': 1000}
        student = request.POST.get('student')
        class_id = request.POST.get('class_')
        student1 = json.loads(student)

        if len(student1):
            pass
        else:
            ret = {'status': 1001}
        try:
            for student_ in student1:
                class_ = FormatClass.objects.get(id=class_id)
                if User.objects.filter(username=student_, format_class=class_).exists():
                    ret = {'status': 1004}
                else:
                    student_ = User.objects.get(username=student_)
                    student_.format_class.add(class_)
                    student_.save()
                    ret = {'status': 1005}
                #  pro = Production.objects.get(id=production_)
                #  rater_ = Teacher.objects.get(username=option)
                #  ques = CompetitionQuestion.objects.get(production=pro)
                # if QuestionProductionScore.objects.filter(question=ques, production=pro, rater=rater_).exists():
                #     ret = {'status': 1005}
                #  else:
                #     raterpro = QuestionProductionScore(question=ques, production=pro, rater=rater_)
                #     raterpro.save()
                #     ret = {'status': 1004}
        except Exception as e:
            print(e)
            ret = {'status': 1003}
        return HttpResponse(json.dumps(ret))
    return render(request, 'compro_management_admin.html')

@login_required(login_url="/")
def aboutCT(request):
    c = {}
    # 判断是否为老师
    try:
        # 关联（ select_realated ）position获取教师，只执行一次查库操作
        teacher = Teacher.objects.select_related("position").get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        c['render_url'] = "/"
        return render(request, 'aboutCT.html', c)

    c['name'] = teacher.name
    if not teacher.position:
        try:
            general_position = Position.objects.get(name="普通教师")
        except Exception:
            general_position = Position.objects.create(name="普通教师",
                                                       permissions=Position.GENERAL_PERMISSION)
        teacher.position = general_position
        teacher.save()
    c['permissions'] = teacher.position.permissions
    # 判断权限中是否有查看作品列表的权限
    if not 'CT_define' in teacher.position.permissions:
        c["no_access"] = "您没有权限查看该版块！"
        c['render_url'] = '/t/index'
    return render(request, 'aboutCT.html', c)

@login_required(login_url="/")
def CTei(request):
    c = {}
    # 判断是否为老师
    try:
        # 关联（ select_realated ）position获取教师，只执行一次查库操作
        teacher = Teacher.objects.select_related("position").get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        c['render_url'] = "/"
        return render(request, 'evaluationinstructions.html', c)

    c['name'] = teacher.name
    if not teacher.position:
        try:
            general_position = Position.objects.get(name="普通教师")
        except Exception:
            general_position = Position.objects.create(name="普通教师",
                                                       permissions=Position.GENERAL_PERMISSION)
        teacher.position = general_position
        teacher.save()
    c['permissions'] = teacher.position.permissions
    # 判断权限中是否有查看作品列表的权限
    if not 'CT_explain' in teacher.position.permissions:
        c["no_access"] = "您没有权限查看该版块！"
        c['render_url'] = '/t/index'
    return render(request, 'evaluationinstructions.html', c)


@login_required(login_url="/")
def aboutUs(request):
    c = {}
    # 判断是否为老师
    try:
        # 关联（ select_realated ）position获取教师，只执行一次查库操作
        teacher = Teacher.objects.select_related("position").get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        c['render_url'] = "/"
        return render(request, 'aboutus.html', c)

    c['name'] = teacher.name
    if not teacher.position:
        try:
            general_position = Position.objects.get(name="普通教师")
        except Exception:
            general_position = Position.objects.create(name="普通教师",
                                                       permissions=Position.GENERAL_PERMISSION)
        teacher.position = general_position
        teacher.save()
    c['permissions'] = teacher.position.permissions
    return render(request, 'aboutus.html', c)


@login_required(login_url="/")
def downloadScratch(request):
    c = {}
    # 判断是否为老师
    try:
        # 关联（ select_realated ）position获取教师，只执行一次查库操作
        teacher = Teacher.objects.select_related("position").get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        c['render_url'] = "/"
        return render(request, 'download_scratch.html', c)

    c['name'] = teacher.name
    if not teacher.position:
        try:
            general_position = Position.objects.get(name="普通教师")
        except Exception:
            general_position = Position.objects.create(name="普通教师",
                                                       permissions=Position.GENERAL_PERMISSION)
        teacher.position = general_position
        teacher.save()
    c['permissions'] = teacher.position.permissions
    # 判断权限中是否有查看作品列表的权限
    if not 'download_scratch_desktop' in teacher.position.permissions:
        c["no_access"] = "您没有权限查看该版块！"
        c['render_url'] = '/t/index'
    return render(request, 'download_scratch.html', c)


@login_required(login_url="/")
def downloadResource(request):
    c = {}
    # 判断是否为老师
    try:
        # 关联（ select_realated ）position获取教师，只执行一次查库操作
        teacher = Teacher.objects.select_related("position").get(username__exact=request.user)
    except Exception as e:
        c['no_access'] = "您不是老师，无权访问！"
        c['render_url'] = "/"
        return render(request, 'download_resource.html', c)

    c['name'] = teacher.name
    if not teacher.position:
        try:
            general_position = Position.objects.get(name="普通教师")
        except Exception:
            general_position = Position.objects.create(name="普通教师",
                                                       permissions=Position.GENERAL_PERMISSION)
        teacher.position = general_position
        teacher.save()
    c['permissions'] = teacher.position.permissions
    # 判断权限中是否有查看作品列表的权限
    if not 'download_data' in teacher.position.permissions:
        c["no_access"] = "您没有权限查看该版块！"
        c['render_url'] = '/t/index'
    return render(request, 'download_resource.html', c)


class apply_management(IsLoginMixin, SingleTableView):
    table_class = ApplyTable
    template_name = "apply_management.html"

    def get_queryset(self):
        try:
            teacher = Teacher.objects.get(username=self.request.user.username)
            if teacher.position.name == "管理员":
                # 管理员获取全部未激活的班级、学校
                apply_class_list = FormatClass.objects.filter(is_active=False)
                apply_school_list = FormatSchool.objects.filter(is_active=False)
            else:
                # 学校负责人查看班级新建申请
                my_school = FormatSchool.objects.filter(chief=teacher, is_active=True)
                apply_class_list = FormatClass.objects.filter(format_school__in=my_school, is_active=False)
                try:
                    # 教研员查找所在地的学校申请
                    adviser = Adviser.objects.get(username=self.request.user.username)
                    apply_school_list = FormatSchool.objects.filter(
                        province=adviser.local_province,
                        city=adviser.local_city,
                        district=adviser.local_district,
                        is_active=False)
                except Exception as e:
                    apply_school_list = FormatSchool.objects.none()
        except Exception as e:
            apply_class_list = FormatClass.objects.none()
            apply_school_list = FormatSchool.objects.none()
        data = [{
            'kind': 'format_class',
            'kind_name': "新建班级",
            'pk': format_class.pk,
            'name': format_class.__str__(),
            'is_interest': format_class.is_interest,
            'chief': format_class.chief.name + "(" + format_class.chief.username + ")"
        } for format_class in apply_class_list]
        data_school = [{
            'kind': 'format_school',
            'kind_name': '新建学校',
            'pk': format_school.pk,
            'name': format_school.__str__(),
            'is_interest': False,
            'chief': format_school.chief.name + "(" + format_school.chief.username + ")"
        } for format_school in apply_school_list]
        data.extend(data_school)
        return data

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # 判断是否为老师
        try:
            # 关联（ select_realated ）position获取教师，只执行一次查库操作
            teacher = Teacher.objects.select_related("position").get(username__exact=self.request.user)
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
                                                           permissions=Position.GENERAL_PERMISSION)
            teacher.position = general_position
            teacher.save()
        context['permissions'] = teacher.position.permissions
        # 判断权限中是否有查看作品列表的权限
        # if not 'batch_signup' in teacher.position.permissions:
        #     context["no_access"] = "您没有权限查看该版块！"
        #     context['render_url'] = '/t/index'
        #     return context

        # 排序
        sort = self.request.GET.get("sort", "")
        if sort:
            context["sort"] = sort
        # 翻页
        try:
            page = self.request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        context["page"] = page

        return context

# -----------------------------------BELOWS ARE API FOR AJAX -----------------------------------------------------------


#教师修改密码
class TeacherChangePasswordView(AuthorRequiredMixin, View):

    def get_object(self):
        pk = self.request.POST.get("username")
        return Teacher.objects.get(username=pk)

    def post(self, request):
        form = TeacherChangePasswordForm(request.POST)
        if form.is_valid():
            teacher = Teacher.objects.get(pk=request.POST.get("username", ""))
            teacher.password = make_password(request.POST.get("new_password1"))
            teacher.save()
            return HttpResponse('{"status": "success", "message": "success"}', content_type="application/json")
        else:
            return HttpResponse(json.dumps(form.errors), content_type="application/json")


@login_required(login_url="/")
def apply_submit(request):
    if request.POST:
        class_list = request.POST.get("class_list", None)
        school_list = request.POST.get("school_list", None)
        result = {}
        class_result = []
        school_result = []
        try:
            teacher = Teacher.objects.get(username=request.user.username)
            class_list = json.loads(class_list)
            if class_list:
                if teacher.position.name == "管理员":
                    format_classes = FormatClass.objects.filter(pk__in=class_list)
                else:
                    my_shcool = FormatSchool.objects.filter(chief=teacher)
                    format_classes = FormatClass.objects.filter(pk__in=class_list, format_school__in=my_shcool)
                for format_class in format_classes:
                    format_class.is_active = True
                    format_class.save()
                    notify.send(sender=request.user, recipient=format_class.chief, actor=request.user,
                                verb="通过了您的班级新建申请",
                                description="您申请新建的班级：" + format_class.__str__() + ", 已经通过审核。")
                    class_result.append(format_class.__str__())
            school_list = json.loads(school_list)
            if school_list:
                if teacher.position.name == "管理员":
                    format_schools = FormatSchool.objects.filter(pk__in=school_list)
                else:
                    adviser = Adviser.objects.get(username=request.user.username)
                    format_schools = FormatSchool.objects.filter(
                        pk__in=school_list,
                        province=adviser.local_province,
                        city=adviser.local_city,
                        district=adviser.local_district,
                        )
                for format_school in format_schools:
                    format_school.is_active = True
                    format_school.save()
                    notify.send(sender=request.user, recipient=format_school.chief, actor=request.user,
                                verb="通过了您的学校新建申请",
                                description="您申请新建的学校：" + format_school.__str__() + ", 已经通过审核。")
                    school_result.append(format_school.__str__())
            result["status"] = "success"
        except Exception as e:
            result["status"] = "fail"
        result["class"] = class_result
        result["school"] = school_result
        return HttpResponse(json.dumps(result), content_type="application/json")

