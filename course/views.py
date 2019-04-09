from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views import View
from dry_rest_permissions.generics import DRYPermissions, DRYPermissionFiltersBase
from rest_framework import status, permissions
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.views.decorators.clickjacking import xframe_options_exempt

from course import models
from course.models import Lesson, Chapter
from course.serializers import LessonSerializer, ChapterSerializer
from scratch_api.models import Teacher, User


def check_course_permission(func):
    def check_auth(request, *args, **kwargs):
        num = request.GET.get("num")
        chapter = request.GET.get("chapter")
        try:
            lesson = Lesson.objects.get(lesson_id=int(num))
            if chapter != "-1":
                chapter_obj = Chapter.objects.get(lesson=lesson, chapter_id=int(chapter))
        except Exception as e:
            return HttpResponse(
                content="{'status': 'fail', 'message': '没有对应课程'}",
                content_type='application/json'
            )
        if lesson.permission == "PR":
            try:
                teacher = Teacher.objects.get(username=request.user.username)
                if lesson.author != teacher:
                    raise ValueError()
                else:
                    return func(request, *args, **kwargs)
            except Exception as e:
                return HttpResponse(
                    content='{"status": "fail", "message": "你没有权限查看该课程"}',
                    content_type='application/json'
                )
        elif lesson.permission == "MC":
            try:
                teacher = Teacher.objects.filter(username=request.user.username)
                if teacher:
                    if lesson.author != teacher.first():
                        raise ValueError()
                else:
                    format_class_id = int(request.GET.get("format_class_id", ""))
                    if format_class_id and format_class_id > 0:
                        user = User.objects.get(username=request.user.username, format_class=format_class_id)
                        for lesson_class in lesson.classes.all():
                            if lesson_class.id == format_class_id:
                                return func(request, *args, **kwargs)
                    raise ValueError()
            except Exception as e:
                return HttpResponse(
                    content='{"status": "fail", "message": "你没有权限查看该课程"}',
                    content_type='application/json'
                )
        return func(request, *args, **kwargs)
    return check_auth


class TOCFilterBackend(DRYPermissionFiltersBase):
    action_routing = False

    def filter_list_queryset(self, request, queryset, view):
        """
        Limits all list requests to only be seen by the owners or creators.
        """
        # return queryset.filter(author=request.user)
        try:
            teacher = Teacher.objects.get(username=request.user.username)
            q_author = queryset.filter(author=teacher)
        except Exception as e:
            pass

        try:
            format_class = int(request.GET.get("format_class", ""))
            #若get参数中有班级，则根据班级来获取课程
            if format_class and format_class > 0:
                q_mc = queryset.filter(permission="MC", classes=format_class)
        except Exception as e:
            pass

        q = queryset.filter(permission='PB')
        try:
            q = q | q_mc
        except Exception as e:
            pass
        try:
            q = q | q_author
        except Exception as e:
            pass
        q = q.order_by("lesson_id").distinct()
        return q


class TOCView(ListAPIView):
    # table of content
    model = Lesson
    # filter_backends = (TOCFilterBackend,)
    # permission_classes = (permissions.AllowAny, )
    permission_classes = (permissions.AllowAny, DRYPermissions)
    serializer_class = LessonSerializer
    filter_backends = (OrderingFilter, TOCFilterBackend, )
    # queryset = Lesson.objects.all()
    ordering_fields = ('lesson_id',)
    ordering = ('lesson_id',)

    def get_queryset(self):
        return Lesson.objects.all()


class LessonListView(View):
    def get(self, request):
        context = {}
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user.username)
            classes = user.format_class.all().order_by("grade", "class_num")
            result = []
            for item in classes:
                obj = {
                    "pk": item.pk,
                    "name": item
                }
                result.append(obj)
            context["classes"] = result
        return render(request, "Scratch/course.html", context)


class LessonView(ListAPIView):
    model = Lesson
    permission_classes = (permissions.AllowAny, )
    serializer_class = LessonSerializer

    def get_queryset(self):
        lesson = self.kwargs.get("lesson")
        return Lesson.objects.filter(lesson_id=lesson)


class ChapterView(ListAPIView):
    model = Chapter
    permission_classes = (permissions.AllowAny, )
    serializer_class = ChapterSerializer

    def get_queryset(self):
        lesson_id = self.kwargs.get("lesson")
        lesson = Lesson.objects.filter(lesson_id=lesson_id)
        if lesson:
            lesson = lesson.first()
            chapter = self.kwargs.get("chapter")
            return Chapter.objects.filter(lesson_id=lesson, chapter_id=chapter)
        else:
            return HttpResponseNotFound()


@xframe_options_exempt
def get_lesson(request, lesson):
    lesson = Lesson.objects.filter(lesson_id=lesson)
    if lesson:
        lesson = lesson.first()
        return HttpResponse(lesson.introduction)
    else:
        return HttpResponseNotFound()


@xframe_options_exempt
def get_chapter(request, lesson, chapter):
    try:
        lesson_obj = Lesson.objects.get(lesson_id=lesson)
    except Exception as e:
        return HttpResponseNotFound()
    chapter = Chapter.objects.filter(lesson=lesson_obj, chapter_id=chapter)
    if chapter:
        chapter = chapter.first()
        return HttpResponse(chapter.content)
    else:
        return HttpResponseNotFound()


@check_course_permission
@xframe_options_exempt
def get_side_course(request):
    if request.method == "GET":
        num = request.GET.get('num')
        chapter = request.GET.get('chapter')
        format_class_id = request.GET.get("format_class_id")
        c = {
            "num": int(num),
            "chapter": int(chapter),
            "format_class_id": int(format_class_id)
        }
        lesson = Lesson.objects.get(lesson_id=int(num))
        c['lesson'] = lesson
        all_chapters = Chapter.objects.filter(lesson=lesson)
        result = []
        for item in all_chapters:
            obj = {
                "chapter_id": item.chapter_id,
                "name": item.name
            }
            result.append(obj)
        c['all_chapters'] = result
        if chapter != "-1":
            c['chapter_obj'] = Chapter.objects.get(lesson=lesson, chapter_id=int(chapter))
            c['chapter_nums'] = Chapter.objects.filter(lesson=lesson).count()
        return render(request, 'Scratch/side_course.html', c)


def insert_behavior(request):
    user = request.GET.get("user")
    lesson_id = request.GET.get("lesson_id")
    chapter_id = request.GET.get("chapter_id")
    start_time = request.GET.get("start_time")
    end_time = request.GET.get("end_time")
    click_audio = request.GET.get("click_audio")
    print(click_audio)
    if click_audio == "true":
        click_audio = True
    else:
        click_audio = False
    obj = models.UserBehaviorLesson(user=user, lesson_id=lesson_id, chapter_id=chapter_id, start_time=start_time, end_time=end_time, click_audio=click_audio)
    obj.save()
    return HttpResponse()
