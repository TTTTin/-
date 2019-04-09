# -*- coding: utf-8 -*-

from rest_framework import serializers
from threadedcomments.models import ThreadedComment

from scratch_api.models import Production, User,Gallery


class MobileAPI_GalleryListSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d")
    update_time = serializers.DateTimeField(format="%Y-%m-%d")
    class Meta:
        model = Gallery
        fields = ['id', 'name', 'is_active', 'author', 'start_time', 'stop_time', 'create_time', 'update_time',
                  'image', 'hit', 'like', 'description']





class MobileAPI_ProductionListSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d")
    update_time = serializers.DateTimeField(format="%Y-%m-%d")
    class Meta:
        model = Production
        fields = ['id', 'name', 'author', 'create_time', 'update_time', 'image', 'hit', 'like']


class MobileAPI_ProductionDetailSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d")
    update_time = serializers.DateTimeField(format="%Y-%m-%d")
    class Meta:
        model = Production
        fields = ['id', 'name', 'author', 'create_time', 'update_time', 'file', 'image',
                  'hit', 'like', 'description', 'operation_instructions', ]


class MobileAPI_FavoriteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Production
        fields = ['id', 'name', 'author', 'image']


class MobileAPI_UserProductionSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d")
    update_time = serializers.DateTimeField(format="%Y-%m-%d")
    class Meta:
        model = Production
        fields = ['id', 'name', 'image', 'create_time', 'update_time']


class MobileAPI_UserInfoSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d")
    class Meta:
        model = User
        fields = ['username', 'name', 'sex', 'grade', 'created_at', 'self_introduction', ]


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer of get Comment
    """
    children = RecursiveSerializer(many=True, read_only=True)
    submit_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ThreadedComment
        fields = ('pk', 'comment', 'parent', 'children', 'submit_date')


class PostCommentSerializer(serializers.ModelSerializer):
    """
    Serializer of post a Comment
    """
    class Meta:
        model = ThreadedComment
        fields = ('content_type', 'object_pk', 'parent', 'comment', 'site', 'user', 'ip_address')
