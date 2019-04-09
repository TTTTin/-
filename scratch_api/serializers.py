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
from .models import User, Production, School, Class, CommentEachOther, AntiCheating, CompetitionQuestion, FormatSchool, \
    FormatClass
from django.utils.translation import ugettext_lazy as _
import re

zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')

# def contain_zh(word):
#     '''
#     判断传入字符串是否包含中文
#     :param word: 待判断字符串
#     :return: True:包含中文  False:不包含中文
#     '''
#     word = word.decode()
#     global zh_pattern
#     match = zh_pattern.search(word)
#
#     return match

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    birthday = serializers.DateField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise ValidationError(detail={'code': '1', 'message': u'重复的用户名'}, code=status.HTTP_409_CONFLICT)
        p = re.findall(r'[\u4e00-\u9fff]+', value)
        print(value, len(p))
        if len(p) != 0:
            raise ValidationError(detail={'code': '3', 'message': u'用户名只能包含字母或数字'}, code=status.HTTP_400_BAD_REQUEST)
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError(detail={'code':'2', 'message':u'密码长度过短'}, code=status.HTTP_400_BAD_REQUEST)
        return value

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            name=validated_data['name'],
            sex=validated_data['sex'],
            birthday=validated_data['birthday'],
            local_province=validated_data['local_province'],
            local_city=validated_data['local_city'],
            local_district=validated_data['local_district'],
            phone_number=validated_data['phone_number']
        )
        user.set_password(validated_data['password'])
        if validated_data['note'] != "":
            user.note = validated_data['note']
        user.save()
        if validated_data['format_school'] != "":
            format_school = validated_data['format_school']
            user.format_school = format_school
        user.save()
        return user

    class Meta:
        model = User
        write_only_fields = ['password']
        fields = ['username', 'password', 'name', 'sex',
                  'birthday', 'local_province', 'local_city', 'local_district',
                  'format_school', 'note',
                  'phone_number']
        extra_kwargs = {
            'school': {'allow_null': True, 'allow_empty': True},
            'school_second': {'allow_null': True, 'allow_empty': True},
        }


class GetUserSchool(serializers.ModelSerializer):
    classes = serializers.StringRelatedField(many=True)
    class Meta:
        model = User
        fields = ['school', 'student_class', 'school_second', 'student_class_second','classes']


class MyAuthTokenSerializer(AuthTokenSerializer):
    """
    custom Serializer that check request auth info
    """

    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                # From Django 1.10 onwards the `authenticate` call simply
                # returns `None` for is_active=False users.
                # (Assuming the default `ModelBackend` authentication backend.)
                if not user.is_active:
                    raise serializers.ValidationError(
                       detail={'username': {'message': u'用户未启用', 'code': '1'}},
                       code='authorization')
            else:
                raise serializers.ValidationError(
                    detail={'username': {'message': u'用户名或密码不正确', 'code': '2'}},
                    code='authorization')
        else:
            raise serializers.ValidationError(
                detail={'username': {'message': u'必须有用户名或密码', 'code': '3'}},
                code='authorization')

        attrs['user'] = user
        return attrs


class AuthTokenSerializerByTrueName(serializers.Serializer):
    name = serializers.CharField(label="Name")
    format_class = serializers.CharField(label="FormatClass")
    password = serializers.CharField(label="Password", style={'input_type': "password"})

    def validate(self, attrs):
        name = attrs.get('name')
        format_class = attrs.get('format_class')
        password = attrs.get('password')
        if name and format_class and password:
            try:
                format_class = FormatClass.objects.get(pk=format_class)
                user = User.objects.filter(name=name, format_class=format_class)
            except Exception:
                raise serializers.ValidationError(
                    detail={'username': {'message': u'填写的信息有误', 'code': 4}},
                    code="authorization"
                )
            if user.count() > 1:
                result = []
                for i in user:
                    obj = {}
                    obj['username'] = i.username
                    obj['birthday'] = i.birthday.strftime("%Y-%m-%d")
                    obj['enrollment_number'] = i.enrollment_number
                    result.append(obj)
                raise serializers.ValidationError(
                    detail={'username': {'message': u"存在多个同名用户", 'code': 5, 'result': json.dumps(result)}},
                    code="authorization"
                )
            user = User.objects.get(name=name, format_class=format_class)
            user = authenticate(username=user, password=password)
            if user:
                # From Django 1.10 onwards the `authenticate` call simply
                # returns `None` for is_active=False users.
                # (Assuming the default `ModelBackend` authentication backend.)
                if not user.is_active:
                    raise serializers.ValidationError(
                       detail={'username': {'message': u'用户未启用', 'code': '1'}},
                       code='authorization')
            else:
                raise serializers.ValidationError(
                    detail={'username': {'message': u'用户名或密码不正确', 'code': '2'}},
                    code='authorization')
        else:
            raise serializers.ValidationError(
                detail={'username': {'message': u'请正确填写信息', 'code': '3'}},
                code='authorization')

        attrs["user"] = user
        return attrs

class AuthTokenSerializerByName(serializers.Serializer):
    """
    custom Serializer that check request auth info according to name
    Warning: Under test
    """

    name = serializers.CharField(label="Name")
    school = serializers.CharField(label="School")
    student_class = serializers.CharField(label="Class")
    password = serializers.CharField(label="Password", style={'input_type': 'password'})

    def validate(self, attrs):
        name = attrs.get('name')
        school = attrs.get('school')
        class_ = attrs.get('student_class')
        password = attrs.get('password')

        if name and school and class_ and password:
            try:
                school_obj = School.objects.get(pk=school)
                class_obj = Class.objects.filter(pk=class_)
                user = User.objects.get(name=name, classes__in=class_obj)
            except Exception:
                raise serializers.ValidationError(
                    detail={'username': {'message': u'填写的信息有误', 'code': '4'}},
                    code='authorization')

            user = authenticate(username=user, password=password)

            if user:
                # From Django 1.10 onwards the `authenticate` call simply
                # returns `None` for is_active=False users.
                # (Assuming the default `ModelBackend` authentication backend.)
                if not user.is_active:
                    raise serializers.ValidationError(
                       detail={'username': {'message': u'用户未启用', 'code': '1'}},
                       code='authorization')
            else:
                raise serializers.ValidationError(
                    detail={'username': {'message': u'用户名或密码不正确', 'code': '2'}},
                    code='authorization')
        else:
            raise serializers.ValidationError(
                detail={'username': {'message': u'请正确填写信息', 'code': '3'}},
                code='authorization')

        attrs['user'] = user
        return attrs


class ProductionCreateSerializer(serializers.ModelSerializer):

    file = serializers.FileField()
    image = serializers.ImageField()
    # author = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        if Production.objects.filter(author__exact=attrs['author'], name__exact=attrs['name']).exists():
            raise serializers.ValidationError(
                detail={'name': {'message': u'该用户已经拥有相同名称的文件', 'code': '1'}})
        return attrs


    class Meta:
        model = Production
        fields = ['author', 'name', 'file', 'update_time', 'create_time', 'image', 'format_class', 'lesson']
        read_only_fields = ()


class ProductionUpdateSerializer(serializers.ModelSerializer):

    file = serializers.FileField()
    image = serializers.ImageField()

    class Meta:
        model = Production
        fields = ['file', 'image', 'format_class']

class CompetitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompetitionQuestion
        fields = ['id', 'quesion']


class ProductionInfoUpdateSerializer(serializers.ModelSerializer):

    tags = serializers.CharField()
    lesson = serializers.CharField(required=False)

    class Meta:
        model = Production
        fields = ['description', 'operation_instructions', 'parent', 'tags', 'lesson']

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        if 'lesson' in validated_data:
            if validated_data['lesson']:
                lesson_id = validated_data.pop('lesson')
            else:
                lesson_id = None
        else:
            # print('awef qw')
            lesson_id = None
        # tags now is a string, we manually transform it to a list
        tags = tags.split(',')
        instance = super().update(instance, validated_data)
        # set tags
        instance.tags.set(*tags, clear=True)
        if lesson_id:
            instance.lesson = Lesson.objects.get(lesson_id=lesson_id)
        else:
            instance.lesson = None
        instance.save()
        return instance

class examProductionInfoUpdateSerializer(serializers.ModelSerializer):

    tags = serializers.CharField()
    # lesson = serializers.CharField(required=False)

    class Meta:
        model = Production
        fields = ['description', 'operation_instructions', 'parent', 'tags']

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        # if 'lesson' in validated_data:
        #     if validated_data['lesson']:
        #         lesson_id = validated_data.pop('lesson')
        #     else:
        #         lesson_id = None
        # else:
        #     # print('awef qw')
        #     lesson_id = None
        # tags now is a string, we manually transform it to a list
        tags = tags.split(',')
        instance = super().update(instance, validated_data)
        # set tags
        instance.tags.set(*tags, clear=True)
        # if lesson_id:
        #     instance.lesson = Lesson.objects.get(lesson_id=lesson_id)
        # else:
        #     instance.lesson = None
        instance.save()
        return instance

class ProductionDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Production
        fields = ['id']
        read_only_fields = ('id', )


class ProductionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Production
        fields = ['id', 'file', 'update_time', 'name', 'image']
        read_only_fields = ('id', 'file', 'update_time')


class SchoolSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        if School.objects.filter(school_name__exact=attrs['school_name']).exists():
            raise serializers.ValidationError(
                detail={'name': {'message': u'学校已经存在', 'code': '1'}})
        return attrs

    class Meta:
        model = School
        fields = ['school_name']


class ClassListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Class
        fields = ('class_name', )


class ClassCreateSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        if Class.objects.filter(school_name__exact=attrs['school_name'], class_name=attrs['class_name']).exists():
            raise serializers.ValidationError(
                detail={'name': {'message': u'学校班级已经存在', 'code': '1'}})
        return attrs

    class Meta:
        model = Class
        fields = ['school_name', 'class_name']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)


class GetClassmateProjectInSameLessonSerializer(serializers.ModelSerializer):

    score = serializers.SerializerMethodField()

    class Meta:
        model = Production
        fields = ['is_active', 'pk', 'image', 'name', 'create_time', 'comment_eachother_all_score', 'score']
        # fields = ('is_active', 'pk', 'image', 'name', 'create_time', 'comment_eachother_all_score')

    def get_score(self, obj):
        # username = self.context['username']
        username = self.context.get('request')
        print(self.context)
        username = username.query_params.get('username')
        user = User.objects.get(username=username)
        if CommentEachOther.objects.filter(user=user, production=obj.pk).exists():
            return CommentEachOther.objects.get(user=user, production=obj).comment_score
        else:
            return 0

# class GetAlreadyPermissions(serializers.ModelSerializer):



class AntiCheatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = AntiCheating
        fields = ['user', 'competition']