# coding=utf-8
from __future__ import unicode_literals
from __future__ import division
import collections
import json

from io import BytesIO
# from StringIO import StringIO
# from io import StringIO
# from StringIO import StringIO
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView,PasswordChangeDoneView
from django.core import serializers
from django.contrib import messages
from django.forms import model_to_dict

from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render_to_response, render, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.context_processors import csrf
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django_tables2 import RequestConfig, SingleTableView
from django.utils.http import urlquote

from course.models import Lesson, Chapter
from scratch_api.mixins import CourseAuthorRequiredMixin
from scratch_api.tables import EProdcutionTable, ProdcutionDownloadTable, ClassTable, UserTable
# from scratch_api.tasks import import_student_excel
# from util.excel import import_student_excel
from .models import Class, Teacher, School, User, Production, TeacherScore, ANTLRScore, ProductionHint
from .forms import MyAuthenticationForm, SignUpForm, UserUpdateForm
from gen.Gen import gen
from .tasks import import_student_excel
# import json

class EMyLoginView(LoginView):
    """
    custom teacher login view
    """
    authentication_form = MyAuthenticationForm
    LOGIN_REDIRECT_URL = 'exam/index'
    redirect_authenticated_user = True
    extra_context = {'class': "form-control"}
    template_name = 'exam/login.html'


class EMyPasswordChangeView(PasswordChangeView):
    success_url = '/eaccounts/password/'
    template_name = 'exam/password_change_form.html'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        try:
            teacher = Teacher.objects.get(pk=self.request.user)
            context['job'] = '评委'
            context['name'] = Teacher.objects.get(pk=self.request.user).name
            context.update(csrf(self.request))
        except Exception as e:
            context['job'] = '选手'
            context['name'] = User.objects.get(pk=self.request.user).name
            context['no_access'] = "您不是老师，无权访问！"
            context.update(csrf(self.request))
        return context
class EPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'exam/password_change_done.html'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        try:
            teacher = Teacher.objects.get(pk=self.request.user)
            context['job'] = '评委'
            context['name'] = Teacher.objects.get(pk=self.request.user).name
        except Exception as e:
            context['job'] = '选手'
            context['name'] = User.objects.get(pk=self.request.user).name
            context['no_access'] = "您不是老师，无权访问！"
        return context



def Esignup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/exam/index')
    else:
        form = SignUpForm()
    return render(request, 'exam/signup.html', {'form': form})

def Elogout(request):
    logout(request)
    return redirect("/exam/")

@login_required(login_url='/exam/')
def Esidebar(request):
    c = {}
    try:
        teacher = Teacher.objects.get(username__exact=request.user)
        c['job'] = '评委'
        c['name'] = teacher.name
    except Exception as e:
        c['job'] = '选手'
        c['name'] = User.objects.get(username__exact=request.user).name
        c['no_access'] = "您不是老师，无权访问！"
    return render(request,"exam/index.html", c)


@login_required(login_url='/exam/')
def Eindex(request):
    # 不是教师禁止进入教师端
    if not Teacher.objects.filter(username=request.user).exists():
        return redirect("/")
    c = {}
    try:
        teacher = Teacher.objects.get(username__exact=request.user)
        c['job'] = '评委'
        c['name'] = teacher.name
    except Exception as e:
        c['job'] = '选手'
        c['name'] = User.objects.get(username__exact=request.user).name
        c['no_access'] = "您不是老师，无权访问！"
    return render(request,"exam/index.html",c)


@login_required(login_url='/exam/')
def Edownload(request):
    c = {}
    # TRY TO GET SCHOOL
    try:
        teacher=Teacher.objects.get(username__exact=request.user)
        c['job']='评委'
        c['name'] = Teacher.objects.get(username__exact=request.user).name
    except Exception as e:
        c['job']='选手'
        c['name']=User.objects.get(username__exact=request.user).name
        c['no_access'] = "您不是老师，无权访问！"
        return render(request,'exam/list.html', c)

    class_ = Class.objects.filter(teacher=teacher)
    schools = class_.values('school_name').distinct()
    school_name = School.objects.filter(school_name__in=schools)
    c['schools'] = school_name
    # ENF OF GET SCHOOL

    school = request.GET.get('school', None)
    class_ = request.GET.get('class', None)
    student = request.GET.get('student', None)
    workname = request.GET.get('workname', None)
    # if provide student
    if student:
        print(student)
        print(Production.objects.filter(author=student))
        production = Production.objects.filter(author__exact=student)
    # if provide class
    elif class_:
        student = User.objects.filter(student_class__exact=class_) | User.objects.filter(
            student_class_second=class_)
        production = Production.objects.filter(author__in=student)
    # if provide school
    elif school:
        class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)
        student = User.objects.filter(student_class__exact=class_) | User.objects.filter(
            student_class_second=class_)
        production = Production.objects.filter(author__in=student)
    # provide nothing
    else:
        class_ = Class.objects.filter(teacher=teacher)
        student = User.objects.filter(student_class__in=class_) | User.objects.filter(
            student_class_second__in=class_)
        production = Production.objects.filter(author__in=student)
    # filter by production name
    if workname and workname != "":
        production = production.filter(name__contains=workname)
    try:
        table = ProdcutionDownloadTable(production)
        RequestConfig(request, paginate={"per_page": 10}).configure(table)
        c['production_table'] = table
    except Exception:
        pass
    c.update(csrf(request))
    return render(request, 'exam/download.html', c)


@login_required(login_url='/exam/')
def Egrade(request):
    c = {}
    # TRY TO GET SCHOOL
    try:
        teacher = Teacher.objects.get(username__exact=request.user)
        c['job'] = '评委'
        c['name'] = teacher.name
    except Exception as e:
        c['job'] = '选手'
        c['name'] = User.objects.get(username__exact=request.user).name
        c['no_access'] = "您不是老师，无权访问！"
        return render(request,'exam/list.html', c)
    class_ = Class.objects.filter(teacher=teacher)
    schools = class_.values('school_name').distinct()
    school_name = School.objects.filter(school_name__in=schools)
    c['schools'] = school_name
    # ENF OF GET SCHOOL

    school = request.GET.get('school', None)
    class_ = request.GET.get('class', None)
    student = request.GET.get('student', None)
    workname = request.GET.get('workname', None)
    # if provide student
    if student:
        production = Production.objects.filter(author__exact=student)
    # if provide class
    elif class_:
        student = User.objects.filter(student_class__exact=class_) | User.objects.filter(
            student_class_second=class_)
        production = Production.objects.filter(author__in=student)
    # if provide school
    elif school:
        class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)
        student = User.objects.filter(student_class__exact=class_) | User.objects.filter(
            student_class_second=class_)
        production = Production.objects.filter(author__in=student)
    # provide nothing
    else:
        class_ = Class.objects.filter(teacher=teacher)
        student = User.objects.filter(student_class__in=class_) | User.objects.filter(
            student_class_second__in=class_)
        production = Production.objects.filter(author__in=student)
    # filter by production name
    if workname and workname != "":
        production = production.filter(name__contains=workname)

    # 取出尚未评分的object
    production = production.filter(teacherscore__isnull=True)
    try:
        table = EProdcutionTable(production)
        RequestConfig(request, paginate={"per_page": 10}).configure(table)
        c['production_table'] = table
    except Exception:
        pass
    c.update(csrf(request))
    return render(request, 'exam/grade.html', c)


def Egenerate_dict_production(raw):
    result = {key: {'score':value, 'percentage': "{:.2f}".format(value/3*100)+"%" } for key, value in raw.items()}
    for key, value in result.items():
        if value['score'] == 0:
            value['class_name'] = 'progress-bar progress-bar-primary'
        elif value['score'] == 1:
            value['class_name'] = 'progress-bar progress-bar-success'
        elif value['score'] == 2:
            value['class_name'] = 'progress-bar progress-bar-warning'
        else:
            value['class_name'] = 'progress-bar progress-bar-danger'
    result['ap_score']['name'] = '抽象化得分'
    result['user_interactivity_score']['name'] = '用户交互得分'
    result['data_representation_score']['name'] = '数据表示得分'
    result['logical_thinking_score']['name'] = '逻辑性得分'
    result['parallelism_score']['name'] = '并行得分'
    result['synchronization_score']['name'] = '同步性得分'
    result['flow_control_score']['name'] = '流控制得分'
    return result


def Egenerate_dict_test(raw):

    result = {key: {'score':value, 'percentage': "{:.2f}".format(value/3*100)+"%" } for key, value in raw.items()}
    for key, value in result.items():
        if value['score'] == 0:
            value['class_name'] = 'progress-bar progress-bar-primary'
        elif value['score'] == 1:
            value['class_name'] = 'progress-bar progress-bar-success'
        elif value['score'] == 2:
            value['class_name'] = 'progress-bar progress-bar-warning'
        else:
            value['class_name'] = 'progress-bar progress-bar-danger'
    result['Abstraction']['name'] = '抽象化得分'
    result['UserInteractivity']['name'] = '用户交互得分'
    result['DataRepresentation']['name'] = '数据表示得分'
    result['LogicalThinking']['name'] = '逻辑性得分'
    result['Parallelism']['name'] = '并行得分'
    result['Synchronization']['name'] = '同步性得分'
    result['FlowControl']['name'] = '流控制得分'
    return result


@login_required(login_url='/exam/')
def Eproduction(request, id):
    c = {}
    try:
        production = Production.objects.get(id=id)
        c['url'] = production.file.url
        teacher = Teacher.objects.get(username__exact=request.user)
        c['job'] = '评委'
        c['name'] = teacher.name
    except Exception:
        c['job'] = '选手'
        c['name'] = User.objects.get(username__exact=request.user).name
        c['no_access'] = "您不是老师，无权访问！"
        return HttpResponseRedirect('exam/index/')
    if request.method == "POST":
        new_score = request.POST['new_score']
        new_comment = request.POST['new_comment']
        object = TeacherScore(production_id=production, score=int(new_score), comment=new_comment)
        object.save()

    if TeacherScore.objects.filter(production_id = production).exists():
        teacher_score = TeacherScore.objects.get(production_id__exact=id)
        c['teacher_score'] = teacher_score
    try:
        print(id)
        print(ANTLRScore.objects)
        antlr_score = ANTLRScore.objects.get(production_id=id)
        print(antlr_score)
        score = model_to_dict(antlr_score, fields=['ap_score', 'parallelism_score', 'synchronization_score',
                                                   'flow_control_score', 'user_interactivity_score',
                                                   'logical_thinking_score', 'data_representation_score'])
        print(score)
        score_dict = Egenerate_dict_production(score)
        c['antlr_score'] = score_dict
        total_score = sum(score.values())
        c['total_score'] = total_score
        production_hints = ProductionHint.objects.filter(production_id=id)
        c['production_hints'] = production_hints
        name = Teacher.objects.get(username__exact=request.user).name
        c['name'] = name
    except Exception as e:
        print(e)
        print("some error happen!")
    c.update(csrf(request))
    return render(request,'exam/production.html', c)


@login_required(login_url='/exam/')
def Elist(request):
    c = {}
    # TRY TO GET SCHOOL
    try:
        teacher = Teacher.objects.get(username__exact=request.user)
        c['job'] = '评委'
        c['name'] = teacher.name
    except Exception as e:
        c['job'] = '选手'
        c['name'] = User.objects.get(username__exact=request.user).name
        c['no_access'] = "您不是老师，无权访问！"
        return render_to_response('exam/list.html', c)
    class_ = Class.objects.filter(teacher=teacher)
    schools = class_.values('school_name').distinct()
    school_name = School.objects.filter(school_name__in=schools)
    c['schools'] = school_name
    # ENF OF GET SCHOOL

    school = request.GET.get('school', None)
    class_ = request.GET.get('class', None)
    student = request.GET.get('student', None)
    workname = request.GET.get('workname', None)
    # if provide student
    if student:
        production = Production.objects.filter(author__exact=student)
    # if provide class
    elif class_:
        student = User.objects.filter(student_class__exact=class_) | User.objects.filter(
            student_class_second=class_)
        production = Production.objects.filter(author__in=student)
    # if provide school
    elif school:
        class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)
        student = User.objects.filter(student_class__exact=class_) | User.objects.filter(
            student_class_second=class_)
        production = Production.objects.filter(author__in=student)
    # provide nothing
    else:
        class_ = Class.objects.filter(teacher=teacher)
        student = User.objects.filter(student_class__in=class_) | User.objects.filter(
            student_class_second__in=class_)
        production = Production.objects.filter(author__in=student)
    # filter by production name
    if workname and workname != "":
        production = production.filter(name__contains=workname)

    # 取出已经评分的object
    production = production.filter(teacherscore__isnull=False)
    try:
        table = EProdcutionTable(production)
        RequestConfig(request, paginate={"per_page": 10}).configure(table)
        c['production_table'] = table
    except Exception:
        pass
    c.update(csrf(request))
    return render(request, 'exam/list.html', c)

class ECourseList(LoginRequiredMixin, ListView):
    login_url = '/exam/'
    model = Lesson
    template_name = "exam/course_management.html"
    context_object_name = "lessons"
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        return Lesson.objects.filter(author=user)

    def get_context_data(self, **kwargs):
        queryset = kwargs.pop('object_list', self.object_list)
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        c={}
        try:
            teacher = Teacher.objects.get(username__exact=self.request.user)
            c['job'] = '评委'
            c['name'] = teacher.name
        except Exception as e:
            c['job'] = '选手'
            c['name'] = User.objects.get(username__exact=self.request.user).name
            # c['no_access'] = "您不是老师，无权访问！"
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset,
                'name': c['name']
                # 'name':User.objects.get(username__exact=self.request.user).name

            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset,
                'name': c['name']
                # 'name': User.objects.get(username__exact=self.request.user).name
            }
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        return context

class EGetCourse(LoginRequiredMixin, ListView):
    login_url = '/exam/'
    model = Lesson
    template_name = "exam/course_management.html"
    context_object_name = "lessons"
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        target = self.request.GET.get('target', None)
        return Lesson.objects.filter(author=user).filter(name=target)


    def get_context_data(self, **kwargs):
        queryset = kwargs.pop('object_list', self.object_list)
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        c={}
        try:
            teacher = Teacher.objects.get(username__exact=self.request.user)
            c['job'] = '评委'
            c['name'] = teacher.name
        except Exception as e:
            c['job'] = '选手'
            c['name'] = User.objects.get(username__exact=self.request.user).name
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset,
                'name':c['name']
                # 'name':Teacher.objects.get(username__exact=self.request.user).name

            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset,
                'name':c['name']
                # 'name': Teacher.objects.get(username__exact=self.request.user).name
            }
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        return context

class ECourseCreate(LoginRequiredMixin, CreateView):
    # if you want to custom or modify default form, change form_class parameter
    #     form_class = ContactForm
    login_url = '/exam/'
    success_url = '/exam/course_management/'
    model = Lesson
    template_name = "exam/course_management_new.html"
    fields = ['name', 'introduction', 'short_introduction', 'permission']

    def form_valid(self, form):
        # we need to add author field
        user = self.request.user
        teacher = Teacher.objects.get(username=user)
        form.instance.author = teacher
        return super(ECourseCreate, self).form_valid(form)
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        try:
            teacher = Teacher.objects.get(username__exact=self.request.user)
            context['job'] = '评委'
            context['name'] = teacher.name
        except Exception as e:
            context['job'] = '选手'
            context['name'] = User.objects.get(username__exact=self.request.user).name
        # context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        return context


class ECourseUpdate(CourseAuthorRequiredMixin, UpdateView):
    login_url = '/exam/'
    model = Lesson
    fields = ['name', 'introduction', 'short_introduction', 'permission']
    template_name = "exam/course_management_update.html"
    success_url = '/exam/course_management/'

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
        try:
            teacher = Teacher.objects.get(username__exact=self.request.user)
            context['job'] = '评委'
            context['name'] = teacher.name
        except Exception as e:
            context['job'] = '选手'
            context['name'] = User.objects.get(username__exact=self.request.user).name
        # context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        return context


class ECourseDelete(DeleteView):
    template_name = "exam/course_management_delete.html"
    model = Lesson
    success_url = '/exam/course_management/'

    def get_object(self, queryset=None):
        try:
            lesson_id = self.kwargs.get("lesson")
            return Lesson.objects.get(lesson_id=lesson_id)
        except Exception as e:
            return None

    def get_success_url(self):
        return "/exam/course_management/"
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        try:
            teacher = Teacher.objects.get(username__exact=self.request.user)
            context['job'] = '评委'
            context['name'] = teacher.name
        except Exception as e:
            context['job'] = '选手'
            context['name'] = User.objects.get(username__exact=self.request.user).name
        # context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        return context

class EChapterList(CourseAuthorRequiredMixin, ListView):
    login_url = '/exam/'
    model = Chapter
    template_name = "exam/chapter_management.html"
    context_object_name = "chapters"
    paginate_by = 8

    def get_queryset(self):
        lesson_id = self.kwargs.get("lesson")
        lesson = Lesson.objects.filter(lesson_id=lesson_id)
        if lesson:
            return Chapter.objects.filter(lesson=lesson)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        try:
            teacher = Teacher.objects.get(username__exact=self.request.user)
            context['job'] = '评委'
            context['name'] = teacher.name
        except Exception as e:
            context['job'] = '选手'
            context['name'] = User.objects.get(username__exact=self.request.user).name
        # context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        context['lesson_id'] = self.kwargs.get("lesson")
        return context

class EGetChapter(LoginRequiredMixin, ListView):
    login_url = '/exam/'
    model = Chapter
    template_name = "exam/chapter_management.html"
    context_object_name = "chapters"
    paginate_by = 8

    def get_queryset(self):
        target = self.request.GET.get('target', None)
        lesson_id = self.kwargs.get("lesson")
        lesson = Lesson.objects.filter(lesson_id=lesson_id)
        if lesson:
            return Chapter.objects.filter(lesson=lesson).filter(name=target)
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        try:
            teacher = Teacher.objects.get(username__exact=self.request.user)
            context['job'] = '评委'
            context['name'] = teacher.name
        except Exception as e:
            context['job'] = '选手'
            context['name'] = User.objects.get(username__exact=self.request.user).name
        # context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        context['lesson_id'] = self.kwargs.get("lesson")
        return context



class EChapterCreate(CourseAuthorRequiredMixin, CreateView):
    login_url = '/exam/'
    model = Chapter
    template_name = "exam/chapter_management_new.html"
    fields = ['chapter_id', 'name', 'content', 'audio']
    success_url = '/exam/course_management/'

    def form_valid(self, form):
        try:
            # we need to add lesson field
            lesson = Lesson.objects.get(lesson_id=self.kwargs.get("lesson"))
            form.instance.lesson = lesson
            return super(EChapterCreate, self).form_valid(form)
        except Exception as e:
            return None

    def get_success_url(self):
        return "/exam/chapter_management/" + self.kwargs.get("lesson") + '/'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        try:
            teacher = Teacher.objects.get(username__exact=self.request.user)
            context['job'] = '评委'
            context['name'] = teacher.name
        except Exception as e:
            context['job'] = '选手'
            context['name'] = User.objects.get(username__exact=self.request.user).name
        # context['name'] = Teacher.objects.get(username__exact=self.request.user).name

        lesson_id = self.kwargs.get("lesson")
        lesson = Lesson.objects.get(lesson_id=lesson_id)
        context['lesson']=lesson
        return context


class EChapterUpdate(CourseAuthorRequiredMixin, UpdateView):
    login_url = '/exam/'
    model = Chapter
    fields = ['chapter_id', 'name', 'content', 'audio']
    template_name = "exam/chapter_management_update.html"

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
        return "/exam/chapter_management/" + self.kwargs.get("lesson") + '/'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        try:
            teacher = Teacher.objects.get(username__exact=self.request.user)
            context['job'] = '评委'
            context['name'] = teacher.name
        except Exception as e:
            context['job'] = '选手'
            context['name'] = User.objects.get(username__exact=self.request.user).name
        # context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        return context


class EChapterDelete(DeleteView):
    template_name = "exam/chapter_management_delete.html"
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
        return "/exam/chapter_management/" + self.kwargs.get("lesson") + '/'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the context
        try:
            teacher = Teacher.objects.get(username__exact=self.request.user)
            context['job'] = '评委'
            context['name'] = teacher.name
        except Exception as e:
            context['job'] = '选手'
            context['name'] = User.objects.get(username__exact=self.request.user).name
        # context['name'] = Teacher.objects.get(username__exact=self.request.user).name
        return context


# ---------------------BELOWS ARE API FOR AJAX -----------------------------------------------------------

def Eajax_school(request):
    teacher = Teacher.objects.get(username__exact=request.user)
    class_ = Class.objects.filter(teacher=teacher)
    schools = class_.values('school_name').distinct()
    school_name = School.objects.filter(school_name__in=schools)
    result = json.dumps(school_name)
    return HttpResponse(result, content_type='application/json')


# def ajax_class(request):
#     school = request.GET.get('school')
#     teacher = Teacher.objects.get(username__exact=request.user)
#     class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)
#     response = serializers.serialize("json", class_)
#     return HttpResponse(response, content_type='application/json')


def Eajax_class(request):
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


def Eajax_student(request):
    class_ = request.GET.get('class')
    # print(class_)
    if not class_:
        return HttpResponse("[]", content_type='application/json')
    student = User.objects.filter(student_class__exact = class_) | User.objects.filter(student_class_second = class_)
    if student:
        response = serializers.serialize("json", student)
        # print(response)
        return HttpResponse(response, content_type='application/json')
    else:
        return HttpResponse("[]", content_type='application/json')


def Eajax_production(request):
    name = request.GET.get('name')
    student = request.GET.get('student')
    class_ = request.GET.get('class')
    school = request.GET.get('school')
    if student:
        production = Production.objects.filter(author__exact=student)
    elif class_:
        student = User.objects.filter(student_class__exact=class_) | User.objects.filter(student_class_second=class_)
        production = Production.objects.filter(author__in=student)
    else:
        teacher = Teacher.objects.get(username__exact=request.user)
        class_ = Class.objects.filter(teacher=teacher).filter(school_name__exact=school)
        student = User.objects.filter(student_class__exact=class_) | User.objects.filter(student_class_second=class_)
        production = Production.objects.filter(author__in=student)
    if name:
        production = production.filter(name__contains=name)
    response = serializers.serialize("json", production)
    return HttpResponse(response, content_type='application/json')

# ---------------------END OF API FOR AJAX -----------------------------------------------------------
