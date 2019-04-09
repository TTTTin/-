# coding=utf-8
from __future__ import unicode_literals
from __future__ import division
import collections
import json
from collections import defaultdict

import xlwt
from io import BytesIO, StringIO
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
from scratch_api.mixins import CourseAuthorRequiredMixin, ProblemAuthorRequiredMixin, CompetitionUserAuthorRequiredMixin
from scratch_api.tables import ProdcutionTable, ProdcutionGradeTable, ProdcutionDownloadTable, ClassTable, UserTable, \
    CourseTable, ChapterTable, ProblemTable, TestCasesTable
from scratch_api.mixins import CourseAuthorRequiredMixin, CompetitionAuthorRequiredMixin
from scratch_api.tables import ProdcutionTable, ProdcutionGradeTable, ProdcutionDownloadTable, ClassTable, UserTable, \
    CourseTable, ChapterTable, TeacherTable, CompetitionTable, ComProTable, CompetitionAdminTable, ComProAdminTable, \
    CompetitionAdviserTable, \
    UserListTable, ComUserTable, ComProAdviserTable, ComProgressTable, ComProScoreTable
# from scratch_api.tasks import import_student_excel
# from util.excel import import_student_excel
from scratch_api.models import Class, Teacher, School, User, Production, TeacherScore, CommentEachOther, ANTLRScore, \
    CompetitionUser, \
    ProductionHint, Production_profile, Position, Competition, CompetitionQuestion, QuestionProductionScore, Adviser, \
    FormatSchool
from scratch_api.forms import MyAuthenticationForm, SignUpForm, UserUpdateForm, TeacherSettingForm
from gen.Gen import gen
from scratch_api.tasks import import_student_excel, import_competition_user_excel, import_teacher_excel, \
    upload_QuesProScore, \
    import_school_excel
from OJ.models import Problem, TestCase, TESTCASE_DIR, generate_testcase_info
from django.apps import apps
from guardian.shortcuts import remove_perm, assign_perm
from django.db.models import Q, Avg, Count, F, Case, When, FloatField, IntegerField, Max

import os


class ProblemList(SingleTableView):
    model = Problem
    table_class = ProblemTable
    template_name = "problem_management.html"

    def get_queryset(self):
        user = self.request.user
        return Problem.objects.filter(author=user)

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
        return table

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


class GetProblem(SingleTableView):
    model = Problem
    table_class = ProblemTable
    template_name = "problem_management.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['title'] = Teacher.objects.get(username__exact=self.request.user).name
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

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
        return table

    def get_queryset(self):
        user = self.request.user
        target = self.request.GET.get('target', None)
        return Problem.objects.filter(author=user).filter(title=target)


class ProblemCreate(LoginRequiredMixin, CreateView):
    # if you want to custom or modify default form, change form_class parameter
    #     form_class = ContactForm
    login_url = '/t/'
    success_url = '/OJ/problem_management/'
    model = Problem
    template_name = "problem_management_new.html"
    fields = ['title', 'description', 'input_description', 'output_description', 'hint', 'permission', 'classes',
              'time_limit', 'memory_limit', 'level', 'tags', ]

    def form_valid(self, form):
        # we need to add author field
        user = self.request.user
        teacher = Teacher.objects.get(username=user)
        form.instance.author = teacher
        return super(ProblemCreate, self).form_valid(form)

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


class ProblemUpdate(ProblemAuthorRequiredMixin, UpdateView):
    login_url = '/t/'
    model = Problem
    fields = ['title', 'description', 'input_description', 'output_description', 'hint', 'permission', 'classes',
              'time_limit', 'memory_limit', 'level', 'tags', ]
    template_name = "problem_management_update.html"
    success_url = '/OJ/problem_management/'

    def get_object(self, queryset=None):
        try:
            problem_id = self.kwargs.get("problem")
            return Problem.objects.get(id=problem_id)
        except Exception as e:
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


class ProblemDelete(DeleteView):
    template_name = "problem_management_delete.html"
    model = Problem
    success_url = '/OJ/problem_management/'

    def get_object(self, queryset=None):
        try:
            problem_id = self.kwargs.get("problem")
            return Problem.objects.get(id=problem_id)
        except Exception as e:
            return None

    def get_success_url(self):
        return "/OJ/problem_management/"

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


class TestCasesList(SingleTableView):
    model = TestCase
    table_class = TestCasesTable
    template_name = "test_cases_management.html"

    def get_queryset(self):
        problem_id = self.kwargs.get("problem")
        problem1 = Problem.objects.filter(id=problem_id)
        return TestCase.objects.filter(problem=problem1)

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        context['id'] = self.kwargs.get("problem")
        problem_id = self.kwargs.get("problem")
        context['title'] = Problem.objects.get(id=problem_id).title
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


class GetTestCases(SingleTableView):
    model = TestCase
    table_class = TestCasesTable
    template_name = "test_cases_management.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        context['id'] = self.kwargs.get("problem")
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

    def get_table(self, **kwargs):
        table = super().get_table()
        RequestConfig(self.request, paginate={"per_page": 12}).configure(table)
        return table

    def get_queryset(self):
        target = self.request.GET.get('target', None)
        problem_id = self.kwargs.get("problem")
        problem1 = Problem.objects.filter(id=problem_id)
        if problem1:
            return TestCase.objects.filter(problem=problem1).filter(name=target)


def test_cases_create(request, problem):
    problem_object = Problem.objects.get(id=problem)
    if request.method == 'POST':
        """
        得到新的测试用例的order
        """
        cases = TestCase.objects.filter(problem=problem_object).all()
        if cases.count() == 0:
            current_order = 0
        else:
            order = cases.aggregate(Max('order'))
            current_order = order.get('order__max') + 1
        current_order_str = str(current_order)

        """
        存储in&out文件
        """
        """
        if TESTCASE_DIR/problem_id not exist
        create  TESTCASE_DIR/problem_id as new dir
        """
        if not os.path.exists(os.path.join(TESTCASE_DIR, str(problem))):
            os.makedirs(os.path.join(TESTCASE_DIR, str(problem)))

        in_data = request.POST.get("in_data", None)
        out_data = request.POST.get("out_data", None)
        action = request.POST.get("add_another", None)
        str1 = str(in_data)
        str2 = str(out_data)
        with open(os.path.join(TESTCASE_DIR, str(problem), str(current_order) + '.in'), 'w', encoding='utf-8') as f:
            f.write(str1)
        with open(os.path.join(TESTCASE_DIR, str(problem), str(current_order) + '.out'), 'w', encoding='utf-8') as f:
            f.write(str2)

        """
        将文件路径写入model的FileField字段中
        """
        new_case = TestCase()
        new_case.problem = Problem.objects.get(id=problem)
        new_case.input_test = problem + '/' + current_order_str + '.in'
        new_case.output_test = problem + '/' + current_order_str + '.out'
        new_case.save()

        """
        redirect to diff pages
        """
        if action is None:
            return HttpResponseRedirect("/OJ/test_cases_management/" + str(problem) + '/')

    name = Teacher.objects.get(username__exact=request.user).name
    if not Teacher.objects.filter(username__exact=request.user).first().position:

        permissions = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage,problem_manage"
        if Position.objects.filter(name='普通教师'):
            Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
        else:
            p = Position.objects.create(name='普通教师',
                                        permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage,problem_manage")
            Teacher.objects.get(username__exact=request.user).position = p
    else:
        permissions = Teacher.objects.filter(
            username__exact=request.user).first().position.permissions
    return render(request, "test_cases_management_new.html",
                  {'problem': problem_object, 'name': name, 'permissions': permissions})


def test_cases_update(request, problem, test_cases):
    problem_belong = Problem.objects.get(id=problem)
    with open(os.path.join(TESTCASE_DIR, str(problem), str(test_cases) + '.in'), 'r') as input_file:
        in_data_r = str(input_file.read())
    with open(os.path.join(TESTCASE_DIR, str(problem), str(test_cases) + '.out'), 'r') as output_file:
        out_data_r = str(output_file.read())
    test_cases_info = {
        'order': test_cases,
        'in_data': in_data_r,
        'out_data': out_data_r,
    }

    if request.method == 'POST':
        in_data = request.POST.get('in_data', None)
        out_data = request.POST.get('out_data', None)
        with open(os.path.join(TESTCASE_DIR, str(problem), str(test_cases) + '.in'), 'w', encoding='utf-8') as f:
            f.write(str(in_data))
        with open(os.path.join(TESTCASE_DIR, str(problem), str(test_cases) + '.out'), 'w', encoding='utf-8') as f:
            f.write(str(out_data))
        generate_testcase_info(problem_belong)
        return HttpResponseRedirect('/OJ/test_cases_management/' + str(problem) + '/')

    name = Teacher.objects.get(username__exact=request.user).name
    if not Teacher.objects.filter(username__exact=request.user).first().position:

        permissions = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage,problem_manage"
        if Position.objects.filter(name='普通教师'):
            Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
        else:
            p = Position.objects.create(name='普通教师',
                                        permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage,problem_manage")
            Teacher.objects.get(username__exact=request.user).position = p
    else:
        permissions = Teacher.objects.filter(
            username__exact=request.user).first().position.permissions

    return render(request, "test_cases_management_update.html",
                  {'problem': problem_belong, "test_case": test_cases_info, 'name': name, 'permissions': permissions})


def test_cases_delete(request, problem, test_cases):
    problem_belong = Problem.objects.get(id=problem)
    if request.method == 'POST':
        current_test_case = TestCase.objects.filter(problem=problem_belong, order=test_cases)
        current_test_case.delete()
        return HttpResponseRedirect('/OJ/test_cases_management/' + str(problem) + '/')

    name = Teacher.objects.get(username__exact=request.user).name
    if not Teacher.objects.filter(username__exact=request.user).first().position:

        permissions = "grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage,problem_manage"
        if Position.objects.filter(name='普通教师'):
            Teacher.objects.get(username__exact=request.user).position = Position.objects.get(name='普通教师')
        else:
            p = Position.objects.create(name='普通教师',
                                        permissions="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage,problem_manage")
            Teacher.objects.get(username__exact=request.user).position = p
    else:
        permissions = Teacher.objects.filter(
            username__exact=request.user).first().position.permissions
    return render(request, "test_cases_management_delete.html",
                  {'problem': problem_belong, 'test_case_order': test_cases, 'name': name, 'permissions': permissions})

# class TestCasesCreate(ProblemAuthorRequiredMixin, CreateView):
#     login_url = '/t/'
#     model = TestCase
#     template_name = "test_cases_management_new.html"
#     fields = ['input_test', 'output_test']
#     success_url = '/OJ/test_cases_management/'
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
#         return "/OJ/test_cases_management/" + self.kwargs.get("problem")
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
#         return "/OJ/test_cases_management/" + self.kwargs.get("problem")
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
#         return "/OJ/test_cases_management/" + self.kwargs.get("problem")
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
