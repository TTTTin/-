# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse
from rest_framework import serializers, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.parsers import FileUploadParser
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError

from course.models import Lesson
from .models import Production
from django.utils.translation import ugettext_lazy as _
import re
from .models import ProductionForBattle

class ProductionForBattleCreateSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        return attrs

    class Meta:
        model = ProductionForBattle
        fields = ['production', 'kind_of_battle']

class ProductionCreateSerializer(serializers.ModelSerializer):

    file = serializers.FileField()
    image = serializers.ImageField()

    def validate(self, attrs):
        if Production.objects.filter(author__exact=attrs['author'], name__exact=attrs['name']).exists():
            raise serializers.ValidationError(
                detail={'name': {'message': u'该用户已经拥有相同名称的文件', 'code': '1'}})
        return attrs


    class Meta:
        model = Production
        fields = ['author', 'name', 'file', 'update_time', 'create_time', 'image']
        read_only_fields = ()


class ProductionUpdateSerializer(serializers.ModelSerializer):

    file = serializers.FileField()
    image = serializers.ImageField()

    class Meta:
        model = Production
        fields = ['name', 'file', 'image', 'update_time']


class ProductionDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Production
        fields = ['id']
        read_only_fields = ('id', )

class ProductionForBattleDeleteSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        return attrs

    class Meta:
        model = ProductionForBattle
        fields = ['production', 'kind_of_battle']


