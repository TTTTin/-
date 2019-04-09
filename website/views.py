import json
import time
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.template.context_processors import csrf
from notifications.models import Notification
from notifications.signals import notify
from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from course.models import Lesson
from scratch_api.models import Production, User, Teacher, FavoriteProduction, FavoriteGallery, galleryproduction, \
    FormatClass, Position
from scratch_api.models import Production, User, Teacher, Class,Gallery,DownloadSource,dataVisualization
from website.forms import UserSettingForm,AddClassForm

from website.mixins import AuthorRequiredMixin, IsLoginMixin, MyFormatClassMixin
from django.core import serializers
from django.db.models import Q
from website.serializers import GallerySerializer

from .registry import badges
import time
import datetime
from django.utils.timezone import utc
from django.utils.timezone import localtime


def check_production_permission(func):
    """
    检查用户是否有查看作品的权限
    :param func:
    :return:
    """
    def check_auth(request, *args, **kwargs):
        id = kwargs["id"]
        try:
            production = Production.objects.get(id=id)
        except Exception as e:
            return HttpResponseForbidden(content="没有该作品")
        if production.is_active and not production.is_competition:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(content="您没有权限查看该作品")
    return check_auth


def website_index(request):
    """index page"""
    return render(request, 'Scratch/index.html')


class MoreProductionListView(View):
    def get(self, request):
        offset = int(request.GET.get("offset"))
        order = request.GET.get("order", "-id")
        q = request.GET.get("q")
        type = request.GET.get("type")
        queryset = Production.objects.filter(is_active=True, is_competition=False)
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(author__name__icontains=q))
        if type:
            queryset = queryset.filter(tags__name__in=[type])
        response = {}
        if queryset[offset: offset+13].count() > 12:
            response["is_all"] = False
        else:
            response["is_all"] = True
        queryset = queryset.order_by(order)[offset: offset+12]
        result = []
        for item in queryset:
            obj = {
                'id': str(item.id),
                'image': item.image.url,
                'name': item.name,
                'author': item.author.username,
                'author_name': item.author.name,
                'hit': item.hit,
                'like': item.like,
            }
            result.append(obj)
        response['result'] = result
        return HttpResponse(json.dumps(response), content_type="application/json")


class WebsiteProductionList(ListView):
    """Production List"""
    model = Production
    template_name = "Scratch/productlist.html"
    context_object_name = "test"
    # I don't know why the context_object_name is test
    # paginate_by = 12

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        type = self.request.GET.get('type', None)

        if type == 'yinyue':
            type = '音乐'
        elif type == 'youxi':
            type = '游戏'
        elif type == 'gushi':
            type = '故事'
        elif type == 'donghua':
            type = '动画'
        elif type == 'yishu':
            type = '艺术'
        elif type == 'moni':
            type = '模拟'
        else:
            type = ""
        queryset = Production.objects.filter(is_active=True, is_competition=False)
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(author__name__icontains=q))
        if type:
            queryset = queryset.filter(tags__name__in=[type])
        order = self.request.GET.get('order', '-id')
        #default order by -id
        if queryset.count() > 12:
            queryset = queryset.order_by(order)[:12]
        else:
            queryset = queryset.order_by(order)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.request.GET.get('order', "-id")
        if order != "-id":
            context["order"] = order
        q = self.request.GET.get("q", "")
        context["q"] = q
        type = self.request.GET.get("type", "")
        context["type"] = type
        if self.object_list.count() < 12:
            context["is_all"] = True
        return context

@check_production_permission
def website_productiondetail(request, id):
    c = {}
    test = Production.objects.get(id=id)
    test.hit += 1
    test.save(update_fields=['hit'])
    c['test'] = test
    c['children'] = test.get_descendants(include_self=False)[:5]
    c.update(csrf(request))
    c['tags']=test.tags.all()
    c['url']=test.file.url
    # notify.send just for test notifications, please delete it or annotate it in production
    # if not request.user.is_anonymous():
    #     notify.send(request.user, recipient=request.user, verb='你访问了'+test.author.username+'的'+test.name+'这个作品', description="大吉大利，今晚吃鸡!")
    return render(request, 'Scratch/productdetail.html', c)


# @csrf_exempt
def website_login(request):
    """
    ajax login
    """
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        print(password,username)
        user = authenticate(username=username, password=password)
        response_data = {}
        response_data['role'] = ''
        if user is not None:
            login(request, user)
            response_data['result'] = 'Success!'
        if Teacher.objects.filter(username=user).exists():
            response_data['role'] = 'teacher'
        return HttpResponse(json.dumps(response_data), content_type="application/json")


def website_logout(request):
    """ajax logout"""
    logout(request)
    response_data = {}
    response_data['result'] = 'Success!'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

#
# def website_userpage(request, author):
#     """userpage"""
#     c = {}
#     user = User.objects.get(pk=author)
#     c['user'] = user
#     production = Production.objects.filter(author=user)
#     c['production'] = production
#     c['others_production'] = Production.objects.filter(Q(author=user) & ~Q(name__icontains="竞赛"))
#     c.update(csrf(request))
#     return render(request, 'Scratch/userpage.html', c)


class WebsiteUserPage(ListView):
    """User Page"""
    model = Production
    template_name = "Scratch/userpage.html"
    context_object_name = "production"
    paginate_by = 9

    def get_queryset(self):
        author = self.kwargs['author']
        user = User.objects.get(pk=author)
        q = self.request.GET.get('q', None)
        production = Production.objects.filter(author=user, is_active=True, is_competition=False)
        if q:
            production = production.filter(name__icontains=q)
        order = self.request.GET.get('order', '-id')
        return production.order_by(order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.kwargs['author']
        user = User.objects.get(pk=author)
        context['others_production'] = Production.objects.filter(author=user, is_active=True, is_competition=False)
        context['user'] = user
        order = self.request.GET.get('order', '-id')
        context['order'] = order
        q = self.request.GET.get('q', "")
        if q:
            context['q'] = q
        # 获取班级列表
        classes = user.format_class.all().order_by("grade", "class_num")
        result = []
        for i in classes:
            obj = {}
            obj["pk"] = i.pk
            obj["name"] = i
            result.append(obj)
        context["classes"] = result
        return context


class UserSetting(IsLoginMixin, AuthorRequiredMixin, View):
    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        form = UserSettingForm()
        current = datetime.date.today()
        return render(request, "Scratch/usersetting.html", {
            'user': user,
            'current': current,

        })

    def post(self, request, pk):
        userSettingForm = UserSettingForm(request.POST)
        user = User.objects.get(pk=pk)
        if userSettingForm.is_valid():
            user.name = userSettingForm.cleaned_data['name']
            user.sex = userSettingForm.cleaned_data['sex']
            user.birthday = userSettingForm.cleaned_data['birthday']
            user.local_province = userSettingForm.cleaned_data['local_province']
            user.local_city = userSettingForm.cleaned_data['local_city']
            user.local_district = userSettingForm.cleaned_data['local_district']
            user.format_school = userSettingForm.cleaned_data['format_school']
            user.phone_number = userSettingForm.cleaned_data['phone_number']
            user.note = userSettingForm.cleaned_data['note']
            user.self_introduction = userSettingForm.cleaned_data['self_introduction']
            user.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(userSettingForm.errors), content_type='application/json')

    def get_object(self, queryset=None):
        pk = self.kwargs['pk']
        return User.objects.get(pk=pk)


class StudentAddClass(AuthorRequiredMixin, View):
    model = User
    form_class = AddClassForm

    def post(self, request, *args, **kwargs):
        student = User.objects.get(username=self.request.user)
        formdata = AddClassForm(request.POST)
        teachers=(Class.objects.get(code=formdata.data['classcode']).teacher.all())

        # teacher=Teacher.objects.get_queryset(teacher=Class.objects.get(formdata.data['classcode']).teacher.all())
        # print(teacher)
        try:
            student.classes.add(Class.objects.get(code=formdata.data['classcode']))
            student.save()
            for teacher in teachers:
                # print(teacher)
                # classteacher=Teacher.objects.get(name=teacher)
                # print(classteacher)
                notify.send(sender=student, recipient=teacher, actor=student,verb='加入班级', description="加入"+Class.objects.get(code=formdata.data['classcode']).school_name+"的"+Class.objects.get(code=formdata.data['classcode']).class_name+"班级成功，请确认")
            return HttpResponse('成功')
        except:
            return HttpResponse("班级编号不存在")

    def get(self, request):
        form = AddClassForm
        c = {}
        c['form'] = form
        return render(request, 'Scratch/addclass.html', c)

    def get_object(self, queryset=None):
        return User.objects.get(username = self.request.user)


# def website_myclass(request, author):
#     """myclass"""
#     if request.user.is_anonymous():
#         return redirect('/')
#     classid = request.GET.get("class_id")
#     c = {}
#     if classid:
#         classid = Class.objects.get(pk=classid)
#         user = User.objects.get(username=author)
#         c['user'] = user
#         production = Production.objects.filter(belong_to=classid).order_by('-create_time', )
#         c['production'] = production
#         c.update(csrf(request))
#         print(production)
#     return render(request, 'Scratch/my_class.html', c)

class MyFormatClass(MyFormatClassMixin, ListView):
    """我的课堂新页面"""
    model = Production
    template_name = "Scratch/my_class.html"
    context_object_name = "production"
    paginate_by = 5

    def get_queryset(self):
        format_class_id = int(self.kwargs['pk'])
        class_lesson_id = self.request.GET.get("class_lesson_id", "")
        homework_lesson_id = self.request.GET.get("homework_lesson_id", "")
        if class_lesson_id:
            #查看我的课堂中某个课程的作品
            if format_class_id == 0:
                production = Production.objects.filter(
                    author=self.request.user,
                    lesson=class_lesson_id
                ).order_by("-update_time")
            else:
                production = Production.objects.filter(
                    format_class=format_class_id,
                    lesson=class_lesson_id
                ).order_by("-update_time")
        elif homework_lesson_id:
            #查看某个课程下我的提交作业
            if format_class_id == 0:
                production = Production.objects.filter(
                    author=self.request.user,
                    lesson=homework_lesson_id
                ).order_by("-update_time")
            else:
                production = Production.objects.filter(
                    author=self.request.user,
                    format_class=format_class_id,
                    lesson=homework_lesson_id
                ).order_by("-update_time")
        else:
            production = Production.objects.none()
        return production

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username=self.request.user.username)
        context["user"] = user
        #返回选择的班级课程id
        class_lesson_id = self.request.GET.get("class_lesson_id", "")
        if class_lesson_id:
            class_lesson_id = int(class_lesson_id)
        context["class_lesson_id"] = class_lesson_id
        #返回选择的作业课程id
        homework_lesson_id = self.request.GET.get("homework_lesson_id", "")
        if homework_lesson_id:
            homework_lesson_id = int(homework_lesson_id)
        context["homework_lesson_id"] = homework_lesson_id
        #获取班级列表
        classes = user.format_class.all().order_by("grade", "class_num")
        result = []
        for i in classes:
            obj = {}
            obj["pk"] = i.pk
            obj["name"] = i
            result.append(obj)
        context["classes"] = result

        #获取课程列表
        format_class_id = self.kwargs['pk']
        context["format_class_id"] = int(format_class_id)
        try:
            if format_class_id != "0":
                lesson_mc = Lesson.objects.filter(permission="MC", classes=format_class_id)
            else:
                lesson_mc = Lesson.objects.none()
        except Exception as e:
            lesson_mc = Lesson.objects.none()
            pass
        lessons = Lesson.objects.filter(permission="PB")
        try:
            lessons = lessons | lesson_mc
        except Exception as e:
            pass
        lessons = lessons.order_by("pk").values("pk", "name").distinct()
        context["lessons"] = lessons
        return context


class WebsiteMyClass(ListView):
    """My Class"""
    model = Production
    template_name = "Scratch/my_class.html"
    context_object_name = "production"
    paginate_by = 3

    def get_queryset(self):
        classid = self.request.GET.get("class_id")
        production = Production.objects.none()
        # production = Production.objects.filter(is_active=True, is_competition=False).order_by('-create_time', )
        if classid:
            author = self.kwargs['author']
            # classid = Class.objects.get(pk=classid)
            format_class = FormatClass.objects.get(pk=classid)
            user = User.objects.get(username=author)
            # c['user'] = user
            production = Production.objects.filter(
                format_class=format_class,
                is_active=True,
                is_competition=False
            ).order_by('-create_time', )
        return production

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.kwargs['author']
        user = User.objects.get(pk=author)
        context['user'] = user
        return context


def website_inbox(request):
    return render(request, 'Scratch/inbox.html')


class InboxUnreadList(ListView):
    """Inbox: Unread notifications"""
    model = Notification
    template_name ="Scratch/inbox.html"
    context_object_name = "queryset"
    paginate_by = 12

    def get_queryset(self):
        user=self.request.user
        return user.notifications.unread()


class InboxAllList(ListView):
    """Inbox: all notifications"""
    model = Notification
    template_name ="Scratch/inbox.html"
    context_object_name = "queryset"
    paginate_by = 12

    def get_queryset(self):
        user=self.request.user
        return user.notifications.all()


class InboxDeatil(DetailView):
    """detail notification"""
    model = Notification
    template_name = "Scratch/inbox_detail.html"

    def get_object(self, queryset=None):
        pk = self.kwargs['pk']
        obj = Notification.objects.get(pk=pk)
        obj.mark_as_read()
        return obj


class MyFavoriteList(ListView):
    """My favorite"""
    model = FavoriteProduction
    template_name ="Scratch/my_favorite.html"
    context_object_name = "queryset"
    paginate_by = 12

    def get_queryset(self):
        user=self.request.user
        print(user)
        list = FavoriteProduction.objects.filter(user=user).values('production')
        return Production.objects.filter(pk__in = list)


class ProductionRemixList(ListView):
    """Production remixes"""
    model = FavoriteProduction
    template_name ="Scratch/production_remix.html"
    context_object_name = "queryset"
    paginate_by = 12

    def get_queryset(self):
        pk = self.kwargs['production']
        obj = Production.objects.get(pk=pk)
        return obj.get_descendants(include_self=False)



def remix_tree(request, production):
    c = {}
    obj = Production.objects.get(pk=production)
    c['obj'] = obj
    c['nodes'] = obj.get_family()
    return render(request, template_name='Scratch/remixtree.html', context=c)


class GalleryCreate(CreateView):
    model = Gallery
    # serializer_class = GallerySerializer
    template_name = "Scratch/createGallery.html"
    fields = ['name', 'image', 'description','start_time','stop_time']
    success_url = '/gallerylist/'

    def form_valid(self, form):
        # we need to add author field
        user = self.request.user
        teacher = Teacher.objects.get(username=user)
        form.instance.author = teacher
        return super(GalleryCreate, self).form_valid(form)

    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get a context
    #     context = super().get_context_data(**kwargs)
    #     # Add in the context
    #     context['name'] = Teacher.objects.get(username__exact=self.request.user).name
    #     return context

# class WebsiteGalleryList(ListView):
#     """Production List"""
#     model = Gallery
#     template_name = "Scratch/gallerylist.html"
#     context_object_name = "test"
#     # I don't know why the context_object_name is test
#     paginate_by = 12
#
#     def get_queryset(self):
#
#         queryset = Gallery.objects.filter(isGallery=True)
#         order = self.request.GET.get('order', '-id')
#         # default order by -id
#         return queryset.order_by(order)


class WebsiteGalleryList(ListView):
    """gallery list"""
    model = Gallery
    template_name = "Scratch/gallerylist.html"
    context_object_name = "test"
    # I don't know why the context_object_name is test
    paginate_by = 12

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        # queryset = Gallery.objects.filter(is_active=True,start_time__lte= time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),stop_time__gte=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        queryset = Gallery.objects.filter(is_active=True)
        order = self.request.GET.get('order', '-id')
        #default order by -id
        return queryset

class WebsiteDownloadList(ListView):
    """gallery list"""
    model = DownloadSource
    template_name = "Scratch/downloadlist.html"
    context_object_name = "test"
    # I don't know why the context_object_name is test
    paginate_by = 12

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        # queryset = Gallery.objects.filter(is_active=True,start_time__lte= time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),stop_time__gte=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        queryset = DownloadSource.objects.filter(is_active=True)
        order = self.request.GET.get('order', '-id')
        #default order by -id
        return queryset


class DataVisualizationList(IsLoginMixin, ListView):
    """gallery list"""
    model = dataVisualization
    template_name = "dataVisualizationList.html"
    context_object_name = "test"
    # I don't know why the context_object_name is test
    paginate_by = 12

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        # queryset = Gallery.objects.filter(is_active=True,start_time__lte= time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),stop_time__gte=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        queryset = dataVisualization.objects.filter(is_active=True)
        order = self.request.GET.get('order', '-id')
        #default order by -id
        return queryset

    def get_context_data(self, **kwargs):
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
        if not 'analysis_data' in teacher.position.permissions:
            context["no_access"] = "您没有权限查看该版块！"
            context['render_url'] = '/t/index'
        return context


def DataVisualization(request, id):
    c = {}
    test = dataVisualization.objects.get(id=id)
    c['test'] = test
    return render(request, 'dataVisualization.html', c)

def dataVisualization_competition(request, id):
    c = {}
    test = dataVisualization.objects.get(id=id)
    c['test'] = test
    return render(request, 'dataVisualization_competition.html', c)

def dataVisualization_student(request, id):
    c = {}
    test = dataVisualization.objects.get(id=id)
    c['test'] = test
    return render(request, 'dataVisualization_student.html', c)

def dataVisualization_production(request, id):
    c = {}
    test = dataVisualization.objects.get(id=id)
    c['test'] = test
    return render(request, 'dataVisualization_production.html', c)

def dataVisualization_judge(request, id):
    c = {}
    test = dataVisualization.objects.get(id=id)
    c['test'] = test
    return render(request, 'dataVisualization_judge.html', c)



class WebsiteGalleryDetail(ListView):
    """gallery detail"""
    model = Production
    template_name = "Scratch/gallerydetail.html"
    context_object_name = "test"
    # I don't know why the context_object_name is test
    paginate_by = 12

    def get_queryset(self):
        c = {}
        test = Gallery.objects.get(pk=self.kwargs['id'])
        print(test)
        galleryId = self.kwargs['id']
        production_list = galleryproduction.objects.filter(admin_checked=True,gallery=galleryId ).values('production')
        queryset = Production.objects.filter(pk__in = production_list)
        test.hit += 1
        test.save(update_fields=['hit'])
        c['test'] = test
        c['galleryId'] = galleryId
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        galleryId = self.kwargs['id']
        galleryObject = Gallery.objects.get(id=galleryId)
        context['galleryObject'] = galleryObject
        print(time.mktime(time.localtime(time.time())))
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        print(localtime(now))
        print(localtime(galleryObject.stop_time.replace(tzinfo=utc)))
        print(galleryObject.stop_time)
        print(time.mktime(time.localtime(time.mktime(galleryObject.stop_time.timetuple()))))
        print(time.strftime("%Y-%m-%d %H:%M:%S",galleryObject.stop_time.timetuple()))
        print(time.mktime(galleryObject.start_time.timetuple())+8*3600)
        print(time.mktime(galleryObject.stop_time.timetuple()))
        if int(time.mktime(time.localtime(time.time())))>(int(time.mktime(galleryObject.start_time.timetuple()))+8*3600):
            context['start_result']='true'
        else:
            context['start_result'] = 'false'
        if int(time.mktime(time.localtime(time.time()))) > (int(time.mktime(galleryObject.stop_time.timetuple())+8*3600)):
            context['stop_result'] = 'false'
        else:
            context['stop_result'] = 'true'
        user = self.request.user
        context['user'] = user

        # print(user)
        # print(galleryObject.id)
        return context

# class MyFavoriteGalleryList(ListView):
#     """My favorite"""
#     model = FavoriteProduction
#     template_name ="Scratch/my_favorite.html"
#     context_object_name = "queryset"
#     paginate_by = 12
#
#     def get_queryset(self):
#         user=self.request.user
#         print(user)
#         list = FavoriteProduction.objects.filter(user=user).values('production')
#         return Production.objects.filter(pk__in = list)



def website_submitProductiontToGallery(request, user,gallery_id):
    """submitProductiontToGallery"""
    c = {}
    user = User.objects.get(pk=user)
    c['user'] = user
    production = Production.objects.filter(author=user)
    c['production'] = production
    c.update(csrf(request))
    galleryObject = Gallery.objects.get(pk=gallery_id)
    print('gallery_id:'+gallery_id)
    c['gallery_id'] = gallery_id
    c['galleryObject'] = galleryObject
    return render(request, 'Scratch/submitProductionToGallery.html', c)

#

def submit_result(request,user,gallery_id):
    check_box_list = request.POST.getlist("check_box_list")
    galleryObject = Gallery.objects.get(pk=gallery_id)

    print(check_box_list)
    c = []
    c1 = {}
    for i in check_box_list:
        production = Production.objects.get(pk=i)

        if not galleryproduction.objects.filter(gallery_id=gallery_id,production_id=i).exists() :
            obj = galleryproduction(gallery_id=gallery_id, production_id=i)
            obj.save()
            str1 = '您的作品['+production.name+']' + '添加成功!'
            c.append(str1)

            badges.possibly_award_badge("production_number_awarded", user=request.user)
            print(str1)
            c1['award']='恭喜您获得一枚奖章！'
        else:
            str2 = '您的作品['+production.name+']' + '已存在于专题中，添加失败'
            c.append(str2)
            print(str2)


    c1['list'] = c
    c1['galleryObject'] = galleryObject

    return render(request, 'Scratch/submitProductionToGallery_result.html',c1)

def fucking_idots(request):
    return render(request, 'test_badges.html')



class BigDataLocalJson(ListView):
    # model = Gallery
    # template_name ="Scratch/gallerylist.html"
    # context_object_name = "queryset"
    # paginate_by = 12
    #
    # def get_queryset(self):
    #     # user=self.request.user
    #     # print(user)
    #     list = Gallery.objects.filter(is_active=True).values('production')
    #     return Production.objects.filter(pk__in = list)

    """gallery list"""
    model = Gallery
    template_name = "Scratch/BigDataLocalJson.html"
    context_object_name = "test"
    # I don't know why the context_object_name is test
    paginate_by = 12

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        # type = self.request.GET.get('type', None)

        # if type == 'yinyue':
        #     type = '音乐'
        # elif type == 'youxi':
        #     type = '游戏'
        # elif type == 'gushi':
        #     type = '故事'
        # elif type == 'donghua':
        #     type = '动画'
        # elif type == 'yishu':
        #     type = '艺术'
        # elif type == 'moni':
        #     type = '模拟'


        # queryset = Gallery.objects.filter(is_active=True,start_time__lte= time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),stop_time__gte=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        queryset = Gallery.objects.filter(is_active=True)
        order = self.request.GET.get('order', '-id')
        #default order by -id
        return queryset

class BigDataOnlineJson(ListView):
    # model = Gallery
    # template_name ="Scratch/gallerylist.html"
    # context_object_name = "queryset"
    # paginate_by = 12
    #
    # def get_queryset(self):
    #     # user=self.request.user
    #     # print(user)
    #     list = Gallery.objects.filter(is_active=True).values('production')
    #     return Production.objects.filter(pk__in = list)

    """gallery list"""
    model = Gallery
    template_name = "Scratch/BigDataOnlineJson.html"
    context_object_name = "test"
    # I don't know why the context_object_name is test
    paginate_by = 12

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        # type = self.request.GET.get('type', None)

        # if type == 'yinyue':
        #     type = '音乐'
        # elif type == 'youxi':
        #     type = '游戏'
        # elif type == 'gushi':
        #     type = '故事'
        # elif type == 'donghua':
        #     type = '动画'
        # elif type == 'yishu':
        #     type = '艺术'
        # elif type == 'moni':
        #     type = '模拟'


        # queryset = Gallery.objects.filter(is_active=True,start_time__lte= time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),stop_time__gte=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        queryset = Gallery.objects.filter(is_active=True)
        order = self.request.GET.get('order', '-id')
        #default order by -id
        return queryset