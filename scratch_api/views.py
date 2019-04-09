# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import base64
import os

import io
import urllib
import time

from django.core import serializers
from django.db.models import Avg, F
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, render_to_response
from django.template.context_processors import csrf
from django.views import View
from django.views.generic import ListView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from course.models import Lesson

from .models import User, Production, School, Class, BaseUser, CommentEachOther, Competition, CompetitionQuestion, \
    AntiCheating, CompetitionUser, QuestionProductionScore, Teacher, FormatSchool, FormatClass
from .serializers import UserSerializer, ProductionCreateSerializer, MyAuthTokenSerializer, ProductionDeleteSerializer, \
    ProductionListSerializer, ProductionUpdateSerializer, SchoolSerializer, ClassListSerializer, ClassCreateSerializer, \
    GetUserSchool, ChangePasswordSerializer, ProductionInfoUpdateSerializer, AuthTokenSerializerByName, \
    AntiCheatingSerializer, AuthTokenSerializerByTrueName, \
    GetUserSchool, ChangePasswordSerializer, ProductionInfoUpdateSerializer,examProductionInfoUpdateSerializer, AuthTokenSerializerByName, \
    AntiCheatingSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.exceptions import APIException, ValidationError
from .exception import DuplicateUsername
from rest_framework.authtoken.models import Token
from uuid import uuid4
from .tasks import add, run,count_block
from production_process.tasks import Product_process
from django.shortcuts import render_to_response
import json
#import numpy as np
#import matplotlib.pyplot as plt
#import pandas as pd
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pickle


class CreateUserView(CreateAPIView):
    """
    Create a new User
    """
    model = User
    permission_classes = (permissions.AllowAny, )
    serializer_class = UserSerializer

    def post(self, request):
        data = request.data.copy()
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data={'code': '0', 'message': 'Success!'}, status=status.HTTP_201_CREATED)
        else:
            return Response("Error!", status=status.HTTP_400_BAD_REQUEST)


class MyObtainAuthToken(ObtainAuthToken):
    """
    Login Auth
    In order to return specific code, we rewrite TokenSerializer class
    """
    serializer_class = MyAuthTokenSerializer


class ObtainAuthTokenByName(ObtainAuthToken):
    serializer_class = AuthTokenSerializerByName
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key,'username':user.username})


class ObtainAuthTokenByTrueName(ObtainAuthToken):
    serializer_class = AuthTokenSerializerByTrueName

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username})


#Abandon for merger Update and Create, Remove soon.
# class FileUploadView(APIView):
#     parser_classes = (MultiPartParser, FormParser)
#     model = Production
#     serializer_class = ProductionCreateSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#     # permission_classes = (permissions.AllowAny, )
#
#     def post(self, request, format=None):
#         up_file = request.FILES['file']
#         image = request.FILES['image']
#         serializer = ProductionCreateSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid(raise_exception=True):
#             # serializer.save(author=request.user, file=up_file)
#             serializer.save(file=up_file, image=image)
#         id = Production.objects.get(author__exact=serializer.validated_data['author'],
#                                     name__exact=serializer.validated_data['name']).id
#         return Response(data={'message': "Success!", 'code':  '0', 'id': id}, status=status.HTTP_201_CREATED)


class GetUserSchoolView(ListAPIView):
    """
    get User's school
    """
    def get_queryset(self):
        username = self.request.query_params.get("username", None)
        if username:
            return User.objects.filter(username=username)
        try:
            username = self.request.data['username']
            return User.objects.filter(username=username)
        except Exception as e:
            return None

    def post(self, request, *args, **kwargs):
        self.get_queryset()
        return self.list(request, *args, **kwargs)

    model = User
    permission_classes = (permissions.AllowAny, )
    serializer_class = GetUserSchool


class FileCreateOrUpdateView(APIView):
    """
    Create or Update a file(Production)
    """
    parser_classes = (MultiPartParser, FormParser)
    model = Production
    serializer_class = (ProductionUpdateSerializer, ProductionCreateSerializer,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        up_file = request.FILES['file']
        image = request.FILES['image']
        name = request.data['name']
        production = Production.objects.filter(author__exact=request.user, name__exact=name)
        if production: #update
            production = production.first()
            if request.data['format_class'] == '0':
                request.data['format_class'] = ''
            if production.is_competition is True:
                return Response(data={'message': "iscompetition", 'code': '0'})
            serializer = ProductionUpdateSerializer(instance=production, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(file=up_file, image=image)
            id = production.id
            path = production.file.path
            # put into queue
            run.delay(id, path)
            count_block.delay(id, path)
            Product_process.delay(id, path)
            return Response(data={'message': "Success!", 'code':  '0', 'id': id}, status=status.HTTP_202_ACCEPTED)
        else:   #create
            user = User.objects.get(username__exact=request.user)
            data = request.data
            data['author'] = user
            if data['format_class'] == '0':
                data['format_class'] = ''
            serializer = ProductionCreateSerializer(data=data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save(file=up_file, image=image, author=user)

            production = Production.objects.get(author__exact=user,
                                                name__exact=serializer.validated_data['name'])
            id = production.id
            path = production.file.path
            # put into queue
            run.delay(id, path)
            count_block.delay(id, path)
            #print(id)
            Product_process.delay(id, path)
            #print(id)
            return Response(data={'message': "Success!", 'code': '0', 'id': id}, status=status.HTTP_201_CREATED)


class ExamFileCreateOrUpdateView(APIView):
    """
    Create or Update a file(Production)
    """
    parser_classes = (MultiPartParser, FormParser)
    model = Production
    serializer_class = (ProductionUpdateSerializer, ProductionCreateSerializer,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        up_file = request.FILES['file']
        image = request.FILES['image']
        name = request.data['name']
        competition_id = request.data['competition_id']
        production = Production.objects.filter(author__exact=request.user, name__exact=name)
        competition = Competition.objects.filter(pk = competition_id)
        competitionuser = CompetitionUser.objects.filter(competition = competition,user=request.user)
        if competition and competitionuser:
            competition = competition.first()
            competitionuser = competitionuser.first()
            delay_time = competitionuser.delay_time
            if int(time.mktime(time.localtime(time.time()))) < (int(time.mktime(competition.start_time.timetuple())) + 8 * 3600) or int(time.mktime(time.localtime(time.time()))) > (int(time.mktime(competition.stop_time.timetuple()) + 8 * 3600)+delay_time*60):
                return Response(data = {'message':"竞赛结束，无法提交",'code':'1'},status=status.HTTP_410_GONE)
            else:
                if production: #update
                    production = production.first()
                    request.data['format_class'] = ''
                    serializer = ProductionUpdateSerializer(instance=production, data=request.data)
                    if serializer.is_valid():
                        serializer.save(file=up_file, image=image)
                    id = production.id
                    production.is_competition = True
                    production.save()
                    path = production.file.path
                    return Response(data={'message': "Success!", 'code':  '0', 'id': id}, status=status.HTTP_202_ACCEPTED)
                else:   #create
                    user = User.objects.get(username__exact=request.user)
                    request.data['author'] = user
                    request.data['format_class'] = ''
                    serializer = ProductionCreateSerializer(data=request.data, context={'request': request})
                    if serializer.is_valid(raise_exception=True):
                        serializer.save(file=up_file, image=image, author=user)

                    production = Production.objects.get(author__exact=user,
                                                name__exact=serializer.validated_data['name'])
                    id = production.id
                    production.is_competition = True
                    production.save()
                    path = production.file.path
                    return Response(data={'message': "Success!", 'code': '0', 'id': id}, status=status.HTTP_201_CREATED)
        else:
            return Response(data={'message': "无该竞赛", 'code': '1'}, status=status.HTTP_400_BAD_REQUEST)

class ProductionInfoUpdate(APIView):
    """
    Update infos of a production
    """
    model = Production
    serializer_class = (ProductionInfoUpdateSerializer, examProductionInfoUpdateSerializer)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        id = request.data['id']
        # print(id)
        try:
            production = Production.objects.get(pk=id)
        except Exception:
            return Response("Error1!", status=status.HTTP_400_BAD_REQUEST)
        if production.is_competition is True:
            serializer = examProductionInfoUpdateSerializer(instance=production, data=request.data)
        else:
            serializer = ProductionInfoUpdateSerializer(instance=production, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': "Success!", 'code': '0'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response("Error2!", status=status.HTTP_400_BAD_REQUEST)

class GetProductionDes(APIView):
    model = Production

    def post(self, request, format=None):
        result = {}
        productionid = request.data['productionid']
        try:
            production = Production.objects.filter(pk=productionid)
        except Exception:
            return Response("Error!", status=status.HTTP_400_BAD_REQUEST)
        if production:
            production = production.first()
            result['description'] = production.description
            result['instruction'] = production.operation_instructions
        return Response(result, status=status.HTTP_202_ACCEPTED)

class CompetitionQuestionUpdate(APIView):
    """
    Update infos of a competitionquestion
    """
    def post(self, request, format=None):
        id = request.data['id']
        # competitionid = request.data['competitionid']
        competitionquestionid = request.data['competitionquestionid']
        # print(id)
        try:
            production = Production.objects.get(pk=id)
            # competition = Competition.objects.get(pk=competitionid)
            competitionquestion = CompetitionQuestion.objects.get(question=competitionquestionid)
            print(production)
            print(competitionquestion)
            if production and competitionquestion:
                competitionquestion.production.add(production)
                competitionquestion.save()
                return Response(data={'message': "Success!", 'code': '0'}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response("Error2!", status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response("Error1!", status=status.HTTP_400_BAD_REQUEST)

class FileDeleteView(APIView):
    model = Production
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, format=None):
        production = Production.objects.filter(id__exact=request.data['id']).distinct()
        if production:
            production = production.first()
            if production.is_active:
                id = str(production.id)
                new_name = production.file.path + id
                os.rename(production.file.path, new_name)
                production.file.name = new_name
                production.name = production.name + id
                production.is_active = 0
                production.save()
                return Response(data={'message': "Success!", 'code':  '0'}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response("", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("", status=status.HTTP_400_BAD_REQUEST)


class FileListView(ListAPIView):
    """
    List production
    """
    model = Production
    serializer_class = ProductionListSerializer
    # permission_classes = (permissions.AllowAny,)
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['name', ]
    ordering_fields = ('name', 'update_time')
    ordering = ('-update_time',)

    def list(self, request, *args, **kwargs):
        if self.get_queryset():
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def get_queryset(self):
        """
        :return: the query set of request user and production is alive 
        """
        return Production.objects.filter(author=self.request.user, is_competition = False, is_active=1)

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class ExamListView(ListAPIView):
    """
    ExamList production
    """
    model = Production
    serializer_class = ProductionListSerializer
    # permission_classes = (permissions.AllowAny,)
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['name', ]
    ordering_fields = ('name', 'update_time')
    ordering = ('-update_time',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """
        :return: the query set of request user and production is alive

        """
        # print(self.request.data)
        question = self.request.GET['question']
        return Production.objects.filter(author=self.request.user).filter(is_active=1).filter(competitionquestion__pk=question)

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


def scratch(request):
    return render_to_response("scratch.html");



def analysis(request):
    if request.method == "GET":
        r = add.delay(3, 4)
        c = {}
        c.update(csrf(request))
        return render_to_response("upload_file.html", c)


class FormatSchoolView(View):
    """
    根据省份、城市、地区来获取学校
    """
    def get(self, request):
        province = request.GET.get("province", "")
        city = request.GET.get("city", "")
        district = request.GET.get("district", "")
        if province == "" or city == "" or district == "":
            return HttpResponse("{'status': 'fail', 'msg': '请先选择省份地区'}", content_type='application/json')
        format_schools = FormatSchool.objects.filter(province=province, city=city, district=district, is_active=True)
        data = []
        for item in format_schools:
            arg = {}
            arg['name'] = item.name
            arg['id'] = item.id
            data.append(arg)
        return HttpResponse(json.dumps(data), content_type='application/json')





class SchoolView(ListAPIView):
    """
    创建一个学校或者获取学校列表
    """
    model = School
    permission_classes = (permissions.AllowAny, )
    serializer_class = SchoolSerializer
    queryset = School.objects.all()

    def post(self, request):
        serializer = SchoolSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data={'code': '0', 'message': 'Success!'}, status=status.HTTP_201_CREATED)
        else:
            return Response("Error!", status=status.HTTP_400_BAD_REQUEST)


class ClassListView(ListAPIView):
    """
    获取一个学校的班级列表
    """
    model = Class
    permission_classes = (permissions.AllowAny, )
    serializer_class = ClassListSerializer

    def get_queryset(self):
        schoolname = self.request.data['school_name']
        return Class.objects.filter(school_name=schoolname)

    def post(self, request, *args, **kwargs):
        self.get_queryset()
        return self.list(request, *args, **kwargs)


class ClassCreateView(ListAPIView):
    """
    创建一个班级
    """
    model = Class
    permission_classes = (permissions.AllowAny, )
    serializer_class = ClassCreateSerializer

    def post(self, request):
        serializer = ClassCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data={'code': '0', 'message': 'Success!'}, status=status.HTTP_201_CREATED)
        else:
            return Response("Error!", status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = BaseUser
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.data.get("new_password") != serializer.data.get("new_password_confirm"):
                return Response({"new_password": ["two new password are not equal!"]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response("Success", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.data.get("new_password") != serializer.data.get("new_password_confirm"):
                return Response({"new_password": ["two new password are not equal!"]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response("Success", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_format_classes(request):
    username = request.GET.get("username", "")
    try:
        user = User.objects.get(username=username)
    except Exception as e:
        return HttpResponseBadRequest()
    result = []
    if user:
        classes = user.format_class.all().order_by("grade", "class_num")
        for item in classes:
            school = item.format_school
            obj = {}
            obj['class'] = school.name + "的" + item.get_full_name()
            obj['pk'] = item.pk
            result.append(obj)
    return HttpResponse(json.dumps(result), content_type="application/json")


def get_classes(request):
    username = request.GET.get("username")
    user = User.objects.filter(username=username)
    #teacher = Teacher.objects.filter(username=username)
    result = []
    if user:
        #if not teacher:
        user = user.first()
        classes = user.classes.all()
        for i in classes:
            school = School.objects.filter(pk=i.school_name)
            school = school.first()
            d = {}
            d["class"] = school.school_name + "的" + i.class_name
            d["id"] = i.pk
            result.append(d)
    result = json.dumps(result)
    return HttpResponse(result, content_type='application/json')


def truename_format_school(request):
    name = request.GET.get("name")
    name = urllib.parse.unquote(name)
    user = User.objects.filter(name=name)
    if not user:
        return HttpResponseBadRequest()
    classes = user.first().format_class.all()
    for i in user:
        userClasses = i.format_class.all()
        classes = classes | userClasses
    schools = classes.values("format_school__name", "format_school__pk").distinct()
    result = []
    for item in schools:
        obj = {}
        obj['school'] = item['format_school__name']
        obj['pk'] = item['format_school__pk']
        result.append(obj)
    return HttpResponse(json.dumps(result), content_type="application/json")


def truename_school(request):
    truename = request.GET.get("username")
    username = urllib.parse.unquote(truename)
    # print(username)
    user = User.objects.filter(name=username)
    classes = user.first().classes.all()
    # print(user)
    for i in user:
        userclasses = i.classes.all()
        classes = classes|userclasses
    # print(classes)
    schools = classes.values('school_name').distinct()
    # print(schools)
    school_name = School.objects.filter(school_name__in=schools)
    result = serializers.serialize("json", school_name)
    return HttpResponse(result, content_type='application/json')


def truename_format_class(request):
    truename = request.GET.get('truename')
    school_id = request.GET.get('school_id')
    classes = User.objects.filter(
        name=truename,
        format_class__format_school=school_id
    ).values("format_class").annotate(
        grade=F("format_class__grade"),
        class_num=F("format_class__class_num")
    )
    classes = classes.order_by("grade", "class_num").distinct()
    result = []
    for item in classes:
        obj = {}
        obj['class'] = str(item['grade']) + "年级" + str(item['class_num']) + "班"
        obj["pk"] = item['format_class']
        result.append(obj)
    return HttpResponse(json.dumps(result), content_type="application/json")


def truename_class(request):
    school = request.GET.get('school')
    class_ = Class.objects.filter(school_name__exact=school)
    response = serializers.serialize("json", class_)
    return HttpResponse(response, content_type='application/json')

def get_classmate_project_in_same_lesson(request):
    username = request.GET.get("username")
    lesson_id = request.GET.get("lesson_id")
    lesson = Lesson.objects.get(lesson_id=lesson_id)
    products = Production.objects.filter(lesson=lesson)
    c = []
    user = User.objects.get(username=username)
    print(len(products))
    for i in products:
        d = {}
        d['is_active'] = i.is_active
        d['pk'] = str(i.pk)
        d['img'] = str(i.image)
        d['name'] = i.name
        d['create_time'] = str(i.create_time)
        d['comment_eachother_all_score'] = i.comment_eachother_all_score
        if CommentEachOther.objects.filter(user=user, production=i.pk).exists():
            # c['score'].append(CommentEachOther.objects.get(user=user, production=i).comment_score)
            # score.append(CommentEachOther.objects.get(user=user, production=i).comment_score)
            d['score'] = CommentEachOther.objects.get(user=user, production=i).comment_score
        else:
            d['score'] = 0
        c.append(d)
    print(c)
    c = json.dumps(c)
    return HttpResponse(c, content_type='application/json')

def get_homework_project(request):
    lessonid = request.GET.get("lesson_id")
    user = request.GET.get("username")
    user = User.objects.filter(username=user)
    lesson = Lesson.objects.filter(lesson_id=lessonid)
    projects = Production.objects.filter(author=user, lesson=lesson)
    # response = serializers.serialize("json", projects)
    # serializers = ProductionListSerializer(data=projects)
    # result = {}
    # result['productions'] = []
    # for i in projects:
    #     result['productions'].append(ProductionListSerializer(data=i))
    data = serializers.serialize("json", projects)
    return HttpResponse(data)

def getresult(request):
    check_box_list = request.REQUEST.getlist("check_box_list")
    print(check_box_list)



class CompetitionWebsiteList(ListView):
    model = Competition
    template_name = "Scratch/competitionlist.html"
    context_object_name = "competitions"

    def get_queryset(self):
        # return Competition.objects.all()
        return super(CompetitionWebsiteList, self).get_queryset()

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['time'] = time.time()

#目前已废弃
class CompetitionWebsiteDetail(ListView):#目前已废弃
    model = CompetitionQuestion
    template_name = "Scratch/competition_production_list.html"
    context_object_name = "questions"

    def get_queryset(self):
        competitiontitle = Competition.objects.get(title=self.kwargs['title'])
        questions = CompetitionQuestion.objects.filter(competition=competitiontitle)
        return questions

    # def get_context_data(self, **kwargs):


#目前已废弃
class CompetitionWebsiteSubmit(ListView):#目前已废弃
    model = CompetitionQuestion
    template_name = "Scratch/competition_submit_production.html"
    context_object_name = "productions"

    def get_queryset(self):
        # competitiontitle = Competition.objects.get(title=self.request.GET.get('competition'))
        # questions = CompetitionQuestion.objects.filter(competition=competitiontitle, question=self.request.GET.get('question'))
        # return questions
        return Production.objects.filter(author=self.request.user)

#目前已废弃
def CompetitionWebsiteSubmitResult(request):
    question = request.GET['question']
    productionid = request.GET['productionid']
    production = Production.objects.get(id=productionid)
    Cq = CompetitionQuestion.objects.get(question=question)
    c1={}
    if Cq:
        Cq.production.add(production)
        c1['state'] = "success"
    return HttpResponse(json.dumps(c1), content_type='application/json')
    # return render(request, 'Scratch/competition_submit_production.html',c1 )

def getCompetitionQs(request):
    competition = request.POST['competition']
    questions = CompetitionQuestion.objects.filter(competition__pk = competition)
    result = serializers.serialize("json",questions)
    # print(result)
    return HttpResponse(result, content_type='application/json')


class AntiCheatingView(CreateAPIView):
    """
    USE GUIDE:
    URL: http://127.0.0.1:8000/competition/anti_cheating/
    METHOD: POST
    HEADERS: Authorization: Token ad9d689fe4f62d9e8b2066563900cd0067591d14
    BODYS: competition: 1
    """
    model = AntiCheating
    serializer_class = AntiCheatingSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        base_user = request.user
        if base_user.is_anonymous():
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.get(username= base_user)
            data = request.data
            #print(data)
            data['user'] = user
            serializer = AntiCheatingSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            return HttpResponse(status=status.HTTP_200_OK)

def CompetionIsOver(request):
    competition_id = request.GET['competition']
    competition_user = request.GET['user']
    competition = Competition.objects.filter(pk=competition_id)
    competitionuser = CompetitionUser.objects.filter(competition=competition,user = competition_user)
    # print(request.user)
    result = {}
    if competition and competitionuser:
        competition = competition.first()
        competitionuser = competitionuser.first()
        delay_time = competitionuser.delay_time
        if int(time.mktime(time.localtime(time.time()))) < (int(time.mktime(competition.start_time.timetuple())) + 8 * 3600) or int(time.mktime(time.localtime(time.time()))) > (int(time.mktime(competition.stop_time.timetuple()) + 8 * 3600)+delay_time*60):
            result['state'] = 0
        else:
            result['state'] = 1
        return HttpResponse(json.dumps(result), content_type='application/json')

def GetServerTime(request):
    result = {}
    result['time'] = int(time.mktime(time.localtime(time.time())))
    return HttpResponse(json.dumps(result), content_type='application/json')

def GetProductionId(request):
    """
    获取竞赛作品前30名的学生名单，并拼接成新表
    :param request:
    :return:
    """
    productions = QuestionProductionScore.objects.values('production').annotate(avg_score=Avg('score'),author=F('production__author'),description = F('production__description'),operation_instructions = F('production__operation_instructions'),
                                                                                image=F('production__image'), school=F('production__author__school'), CTscore=F('production__antlrscore__total'), format_school=F('production__author__format_school')).order_by('-avg_score')
    data = []
    for item in productions[:30]:
        item['production'] = str(item['production'])
        data.append(item)
    return HttpResponse(json.dumps(data), content_type='application/json')


