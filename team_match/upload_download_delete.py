
import datetime, re, json
from django.template.context_processors import csrf
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, render, redirect
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from course.models import Lesson
from scratch_api.models import User, Production
# from .models import JrProduction, JrLesson, JrTask
from .serializers import ProductionCreateSerializer, ProductionUpdateSerializer, ProductionForBattleCreateSerializer
import urllib.parse

class DownloadProduction(ListAPIView):

    def post(self, request):
        try:
            production = Production.objects.get(id=request.data['productionID'])
            if production is not None and request.data['username'] == 'admin' or request.data['username'] == production.author.name:
                file = open('media/' + str(production.file), 'rb')
                response = HttpResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename=' + str(production.name.encode('utf-8'))
                response['file-name'] = urllib.parse.quote(production.name)
            else:
                response = HttpResponse()
        except:
            response = HttpResponse()
        return response

class DeleteProduction(ListAPIView):

    def post(self, request):
        ret = {}
        try:
            username, production_id = request.POST['username'], request.POST['productionID']
            user = User.objects.filter(name=username)
            Production.objects.filter(id=production_id, author=user).delete()
            ret['mess'] = '删除成功！'
        except:
            ret['mess'] = '删除失败！'
        return HttpResponse(json.dumps(ret), status=status.HTTP_201_CREATED)



class UploadProduction(APIView):
    parser_classes = (MultiPartParser, FormParser)
    model = Production
    serializer_class = (ProductionUpdateSerializer, ProductionCreateSerializer,)

    def post(self, request, format=None):
        response = dict()
        data = dict()
        context = {}
        user = User.objects.get(name=request.data["author"])
        if not user:
            response['mess'] = 'please sign in'
            return HttpResponse(json.dumps(response), status=status.HTTP_201_CREATED)

        up_file = request.FILES['file']
        data['file'] = up_file

        image = request.FILES['image']
        data['image'] = image

        projectname = request.data['name']
        data['name'] = projectname



        Production.objects.filter(author__exact=user, name__exact=projectname)

        if request.data['uploadType'] == 'update':  # update
            production_id = request.data['productionID']
            production = Production.objects.filter(id=production_id, author=user)
            if production:
                same_name_production = Production.objects.all().exclude(id=production_id).filter(author=user, name=projectname)
                if not same_name_production:
                    production = production.first()
                    data['update_time'] = datetime.datetime.now()
                    serializer = ProductionUpdateSerializer(instance=production, data=data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save(file=up_file)
                        response['mess'] = '上传成功！'
                    else:
                        response['mess'] = '上传失败！'
                else:
                    response['mess'] = '该作品名已存在！'
            else:
                response['mess'] = '不存在你要更新的作品！'
            return HttpResponse(json.dumps(response), status=status.HTTP_202_ACCEPTED)
        else:   # create
            production = Production.objects.filter(name=projectname, author=user)
            if not production:
                data['create_time'] = data['update_time'] = datetime.datetime.now()
                data['author'] = user

                serializer = ProductionCreateSerializer(data=data, context={'request': request})
                battle_serializer = ProductionForBattleCreateSerializer(data={}, context={'request': request})
                if serializer.is_valid(raise_exception=True) and battle_serializer.is_valid(raise_exception=True):
                    serializer.save(file=up_file, image=image)

                    production = Production.objects.filter(author__exact=user, name__exact=projectname).first()

                    if request.data['createType'] == 'gobang':
                        kind_of_battle = 1
                    elif request.data['createType'] == 'snake':
                        kind_of_battle = 2
                    else:
                        kind_of_battle = 0

                    battle_serializer.save(production=production, kind_of_battle=kind_of_battle)

                    response['mess'] = '上传成功！'
                else:
                    response['mess'] = '上传失败！'
            else:
                response['mess'] = '该作品名已存在！'
            return HttpResponse(json.dumps(response), status=status.HTTP_201_CREATED)