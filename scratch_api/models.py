# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from random import randrange

from django.conf import settings
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
from jsonfield import JSONField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, UserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, UserManager, AbstractUser)
from django.utils import timezone
import os

from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase

from scratch_api.storage import OverwriteStorage
from guardian.admin import GuardedModelAdmin
from django.contrib import admin
from ckeditor.fields import RichTextField

CHARSET = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
LENGTH = 6

class MyUserManager(BaseUserManager):
    """
    The default User Model is too crowd, we use Custom BaseUserManager instead
    """

    def create_user(self, username, password=None):
        """
        create a user 
        :param username: username of new User 
        :param password: password of new User
        :return: A BaseUser object
        """

        user = self.model(
            username=username,
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        """
        create a superuser, this is use for "python manage createsuperuser"
        :param username: name of new superuser
        :param password: password of new superuser
        :return: a BaseUser object with is_admin set to True
        """

        user = self.create_user(username, password)
        user.is_admin = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class BaseUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True, primary_key=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ()

    class Meta:
        ordering = ('-username',)

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def is_superuser(self):
        return self.is_admin


class BaseUser2Session(models.Model):
    user = models.OneToOneField(BaseUser, null=False)
    session_key = models.CharField(null=False, max_length=40)


class User(BaseUser):
    """
    用户/学生模型
    """

    name = models.CharField(max_length=30, verbose_name="姓名")
    sex = models.CharField(max_length=30, null=True, verbose_name="性别")
    grade = models.CharField(max_length=30, null=True, blank=True, verbose_name="年级",db_index=True)
    student_id = models.CharField(max_length=30, null=True, blank=True, verbose_name="学号")
    birthday = models.DateField(null=True, blank=True, verbose_name="生日")
    local_province = models.CharField(max_length=30, null=True, blank=True, verbose_name="省份")
    local_city = models.CharField(max_length=30, null=True, blank=True, verbose_name="城市")
    local_district = models.CharField(max_length=30, null=True, blank=True, verbose_name="地区")
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间',db_index=True)
    school = models.ForeignKey('School',verbose_name='学校', max_length=50, null=True, blank=True, related_name='user_school')
    student_class = models.ForeignKey('Class', max_length=30, null=True, blank=True, related_name='user_class',on_delete=models.SET_NULL)
    school_second = models.ForeignKey('School', max_length=50, null=True, blank=True, related_name='user_school_2')
    student_class_second = models.ForeignKey('Class', max_length=30, null=True, blank=True,
                                             related_name='user_class_2',on_delete=models.SET_NULL)
    classes = models.ManyToManyField('Class', blank=True, verbose_name="班级")
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name="手机号")
    self_introduction = models.TextField(verbose_name="个人介绍", null=True, blank=True, default="麦宝真好玩!")
    favorite_production = models.ManyToManyField('Production', blank=True, through='FavoriteProduction')
    favorite_gallery = models.ManyToManyField('Gallery', blank=True, through='FavoriteGallery')
    coding_duration = models.IntegerField(default=0 , verbose_name="用户有效编程总时长")
    comment_eachother = models.ManyToManyField('Production', blank=True, through='CommentEachOther', related_name='score')
    format_school = models.ForeignKey('FormatSchool', verbose_name="所在学校", null=True, blank=True)
    format_class = models.ManyToManyField('FormatClass', verbose_name="所在班级", blank=True)
    enrollment_number = models.CharField(verbose_name='学籍号', max_length=16, null=True, blank=True, unique=True)
    note = JSONField(verbose_name="备注信息", null=True, blank=True)


    class Meta:
        ordering = ('-username',)

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    create a auth token for every User 
    """
    if created:
        Token.objects.create(user=instance)

def get_competition_path(instance,filename):
    return os.path.join(instance.author.username, instance.name + '_' + filename)
def get_upload_path(instance, filename):
    """
    set upload path for Production.file
    """
    # print (os.path.join(instance.author.username, filename))
    return os.path.join(instance.author.username, instance.name+'.sb2')


def get_image_path(instance, filename):
    """
    set upload path for Production.image
    """
    return os.path.join(instance.author.username, instance.name + '_' + filename)


class Position(models.Model):
    # 普通教师权限
    GENERAL_PERMISSION = "grade_production,\
download_production,\
upload_test_production,\
analysis_production,\
analysis_class,\
analysis_data,\
CT_define,\
CT_explain,\
download_scratch_desktop,\
download_data,\
class_manage,\
batch_signup,\
competition_manage,\
competition_user_manage,\
competitionManagement,\
problem_manage,\
admin_manage,\
course_manage"

    name = models.CharField(max_length=100, verbose_name="职位名称")
    permissions = models.CharField(max_length=1000, null=True, blank=True, verbose_name="权限", default="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage")

    def __str__(self):
        return self.name


class Teacher(BaseUser):
    """
    教师模型 
    """
    name = models.CharField(max_length=20, verbose_name="姓名")
    email = models.EmailField(max_length=50, verbose_name="邮箱")
    school = models.CharField(max_length=50, verbose_name="学校", blank=True)
    belong_adviser = models.ForeignKey('Adviser', verbose_name="所属教研员", null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name="电话")
    # permissions = models.CharField(max_length=500, default="grade_production,download_production,upload_test_production,analysis_production,analysis_class,analysis_data,CT_define,CT_explain,download_scratch_desktop,download_data,class_manage,batch_signup,course_manage,admin_manage", blank=True, verbose_name="权限")
    position = models.ForeignKey(Position, null=True, verbose_name="职位")
    format_school = models.ForeignKey('FormatSchool', verbose_name="所属学校", null=True, blank=True)

    class Meta:
        ordering = ('-username',)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    # If you only inherit GenericUUIDTaggedItemBase, you need to define
    # a tag field. e.g.
    # tag = models.ForeignKey(Tag, related_name="uuid_tagged_items", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class Production(MPTTModel):
    """
    作品模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='作品名称',db_index=True)
    author = models.ForeignKey(User, null=True, verbose_name='作者')
    file = models.FileField(upload_to=get_upload_path, verbose_name='下载地址')
    is_active = models.BooleanField(default=True,db_index=True)
    #评委manytomany
    # fix bugs of create_time and update_time
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', db_index=True)
    image = models.ImageField(null=True, upload_to=get_image_path, storage=OverwriteStorage())
    belong_to = models.ForeignKey('Class', null=True, blank=True, on_delete=models.SET_NULL)
    format_class = models.ForeignKey('FormatClass', null=True, blank=True, on_delete=models.SET_NULL)
    hit = models.BigIntegerField(default=0, verbose_name='点击数', db_index=True)
    like = models.BigIntegerField(default=0, verbose_name='点赞数', db_index=True)
    lesson = models.ForeignKey('course.Lesson', null=True, blank=True, verbose_name='课程名称')
    description = models.TextField(verbose_name="作品介绍", blank=True, null=True)
    operation_instructions = models.TextField(verbose_name="操作说明", blank=True, null=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    tags = TaggableManager(through=UUIDTaggedItem, blank=True)
    # tea_score=models.IntegerField(default=0,null=True,verbose_name='教师评分')
    # tea_score = models.ForeignKey('TeacherScore', null=True, blank=True,verbose_name='分数')
    comment_eachother_all_score = models.IntegerField(default=0, verbose_name='互评总分')
    production_duration = models.IntegerField(default=0, verbose_name="作品的有效创作时间")
    script_count = models.IntegerField(default=0, verbose_name="创建的脚本(函数)总数")
    sprite_count = models.IntegerField(default=0, verbose_name="创建的角色总数")
    is_competition = models.BooleanField(default=False, verbose_name="是否属于竞赛", db_index=True)


    def __unicode__(self):
        return self.author.name + ':' + self.name

    def __str__(self):
        return self.author.name + ':' + self.name

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


class ANTLRScore(models.Model):
    """
    ANTLR生成得分模型
    """
    production_id = models.OneToOneField(Production, to_field='id')
    ap_score = models.IntegerField(verbose_name="抽象化")
    parallelism_score = models.IntegerField(verbose_name="并行")
    synchronization_score = models.IntegerField(verbose_name="同步性")
    flow_control_score = models.IntegerField(verbose_name="流控制")
    user_interactivity_score = models.IntegerField(verbose_name="用户交互")
    logical_thinking_score = models.IntegerField(verbose_name="逻辑性")
    data_representation_score = models.IntegerField(verbose_name="数据表示")
    content_score = models.IntegerField(verbose_name="内容", default=0)
    code_organization_score = models.IntegerField(verbose_name="代码组织", default=0)
    total = models.IntegerField(verbose_name="总分", default=0)

    def save(self, *args, **kwargs):
        self.total = self.ap_score + self.synchronization_score + self.parallelism_score \
                    + self.flow_control_score + self.user_interactivity_score + self.logical_thinking_score + \
                    self.data_representation_score + self.content_score + self.code_organization_score
        super(ANTLRScore, self).save(*args, **kwargs)


class Production_profile(models.Model):
    """
    作品的静态统计模型
    """
    production_id = models.OneToOneField(Production, to_field='id')
    motion_num = models.IntegerField(default=0)
    looklike_num = models.IntegerField(default=0)
    sounds_num = models.IntegerField(default=0)
    draw_num = models.IntegerField(default=0)
    event_num = models.IntegerField(default=0)
    control_num = models.IntegerField(default=0)
    sensor_num = models.IntegerField(default=0)
    operate_num = models.IntegerField(default=0)
    more_num = models.IntegerField(default=0)
    data_num = models.IntegerField(default=0)
    sprite_num = models.IntegerField(default=0)
    backdrop_num = models.IntegerField(default=0)
    snd_num = models.IntegerField(default=0)

class ProductionHint(models.Model):
    """
    作品提示模型
    """
    production_id = models.ForeignKey(Production, to_field='id')
    hint = models.CharField(max_length=100)


class TeacherScore(models.Model):
    """
    教师评分模型
    """
    production_id = models.OneToOneField(Production, to_field='id')
    score = models.IntegerField(verbose_name='教师评分')
    comment = models.TextField(null=True, max_length=2000)


class School(models.Model):
    """
    学校模型
    """
    school_name = models.CharField(primary_key=True, max_length=50,db_index=True)

    def __unicode__(self):
        return self.school_name

    def __str__(self):
        return self.school_name


class Class(models.Model):
    """
    班级模型
    """
    id = models.AutoField(primary_key=True)
    school_name = models.ForeignKey(School, to_field='school_name')
    # grade = models.CharField(max_length=30, null=True, blank=True)
    class_name = models.CharField(max_length=40,db_index=True)
    teacher = models.ManyToManyField(Teacher, blank=True)
    code = models.CharField(max_length=LENGTH, editable=False,db_index=True)

    class Meta:
        unique_together = (("school_name", "class_name"),)

    def __unicode__(self):
        return self.school_name.school_name  + u'的' + self.class_name

    def __str__(self):
        return self.school_name.school_name +'的' + self.class_name

    def save(self, *args, **kwargs):
        """
        Upon saving, generate a code by randomly picking LENGTH number of
        characters from CHARSET and concatenating them. If code has already
        been used, repeat until a unique code is found, or fail after trying
        MAX_TRIES number of times. (This will work reliably for even modest
        values of LENGTH and MAX_TRIES, but do check for the exception.)
        Discussion of method: http://stackoverflow.com/questions/2076838/
        """
        unique = False
        while not unique:
            new_code = ''
            for i in range(LENGTH):
                new_code += CHARSET[randrange(0, len(CHARSET))]
            if not Class.objects.filter(code=new_code):
                self.code = new_code
                unique = True
        super(Class, self).save(*args, **kwargs)


class FavoriteProduction(models.Model):
    user = models.ForeignKey('User')
    production = models.ForeignKey('Production')
    favorite_time = models.TimeField(auto_now_add=True, verbose_name="收藏时间")


class LikeProduction(models.Model):
    user = models.ForeignKey('BaseUser', blank=True, null=True)
    token = models.CharField(max_length=50, null=True, blank=True)#token用于匿名用户判断,使用IP和UA的MD5判断
    production = models.ForeignKey('Production')
    favorite_time = models.TimeField(auto_now_add=True, verbose_name="点赞时间")

    class Meta:
        unique_together = [('user', 'production', 'token')]


class CommentEachOther(models.Model):
    user = models.ForeignKey('User')
    production = models.ForeignKey('Production')
    comment_score = models.IntegerField(default=0, verbose_name='评分')


class Gallery(models.Model):
    """
    专题模型
    """
    gallery_production = models.ManyToManyField('Production', blank=True, through='galleryproduction')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='专题名称')
    author = models.ForeignKey(BaseUser, null=True, verbose_name='专题创建者')
    is_active = models.BooleanField(default=True,verbose_name='专题发布状态')
    start_time = models.DateTimeField(verbose_name='专题开始时间',default=timezone.now,editable=True)
    stop_time = models.DateTimeField(verbose_name='专题结束时间',default=timezone.now,editable=True)
    # stop_time = models.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'date'}),verbose_name='专题结束时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='专题创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='专题更新时间')
    image = models.ImageField(null=True, upload_to=get_image_path,verbose_name='专题图片')
    hit = models.BigIntegerField(default=0, verbose_name='专题点击数')
    like = models.BigIntegerField(default=0, verbose_name='专题点赞数')
    description = models.TextField(verbose_name="专题介绍", blank=True, null=True)

    def __unicode__(self):
        return self.author.username + '的' + self.name

    def __str__(self):
        return self.author.username + '的' + self.name

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


class galleryproduction(models.Model):

    admin_checked = models.BooleanField(default=False,verbose_name='管理员是否已审核')
    gallery = models.ForeignKey('Gallery')
    production = models.ForeignKey('Production')


class FavoriteGallery(models.Model):
    """
    专题收藏
    """
    user = models.ForeignKey('User')
    gallery = models.ForeignKey('Gallery')
    favorite_time = models.TimeField(auto_now_add=True, verbose_name="收藏时间")



class LikeGallery(models.Model):
    """
    专题点赞
    """
    user = models.ForeignKey('BaseUser', blank=True, null=True)
    token = models.CharField(max_length=50, null=True, blank=True)#token用于匿名用户判断,使用IP和UA的MD5判断
    gallery = models.ForeignKey('Gallery')
    favorite_time = models.TimeField(auto_now_add=True, verbose_name="点赞时间")

    class Meta:
        unique_together = [('user', 'gallery', 'token')]


class Competition(models.Model):
    """
    竞赛表
    """
    title = models.CharField(verbose_name="竞赛名称", max_length=100, unique=True)
    creator = models.ForeignKey("Teacher", verbose_name="创建者")
    rater = models.ManyToManyField("Teacher", verbose_name="评委", default=creator, related_name="rater")
    user = models.ManyToManyField('User', verbose_name="参赛者", through='CompetitionUser', blank=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    start_time = models.DateTimeField(verbose_name="开始时间", null=True)
    stop_time = models.DateTimeField(verbose_name="结束时间", null=True)
    content = models.FileField(verbose_name="竞赛内容", upload_to="competions/", null=True, blank=True)
    advisers = models.ManyToManyField("adviser", verbose_name="教研员", related_name="advisers")
    # file = models.FileField(upload_to=get_upload_path, storage=OverwriteStorage(), verbose_name='下载地址')
    class Meta:
        verbose_name = "竞赛"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class CompetitionUser(models.Model):
    """
    竞赛用户关联表
    """
    competition = models.ForeignKey('Competition', verbose_name="竞赛")
    user = models.ForeignKey('User', verbose_name="参赛者")
    tutor = models.ForeignKey('Teacher', verbose_name="指导老师", null=True, blank=True)
    delay_time = models.IntegerField(default=0, verbose_name="延迟时间")

    class Meta:
        verbose_name = "竞赛用户关联表"
        verbose_name_plural = verbose_name
        unique_together = (("competition", "user"), )

    def __str__(self):
        return self.competition.title + ": " + self.user.name



class AntiCheating(models.Model):
    """
    用来记录用户跳出页面
    """
    user = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)
    competition = models.ForeignKey(Competition)

    def __str__(self):
        return self.user.username + ':' + self.competition.__str__()


class CompetitionQuestion(models.Model):
    question = models.CharField(verbose_name="题目", max_length=100)
    competition = models.ForeignKey('Competition', verbose_name="所属竞赛")
    production = models.ManyToManyField('Production', verbose_name="作品", blank=True)
    detail = RichTextField(verbose_name="描述", null=True, blank=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    limit_score = models.IntegerField(default=100, verbose_name="满分")
    limit_small_score = JSONField(verbose_name="各维度满分", blank=True, null=True, default=None)

    class Meta:
        verbose_name = "竞赛题目"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.competition.title + ": " + self.question


class QuestionProductionScore(models.Model):
    """
    竞赛作品得分表
    """
    question = models.ForeignKey('CompetitionQuestion', verbose_name="题目")
    production = models.ForeignKey('Production', verbose_name="作品")
    rater = models.ForeignKey('Teacher', verbose_name="评委")
    score = models.IntegerField(verbose_name="得分", null=True, blank=True)
    small_score = JSONField(verbose_name="各维度得分", blank=True, null=True,default=None)
    comment = models.TextField(verbose_name="评语", null=True, blank=True)
    score_time = models.DateTimeField(verbose_name="评分时间", auto_now=True)
    is_adviser = models.BooleanField(default=False, verbose_name="是否为教研员")

    class Meta:
        verbose_name = "竞赛作品得分表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.question.question + ": " + self.production.name + ": " + self.rater.name


class Adviser(Teacher):
    """
        教研员
    """
    local_province = models.CharField(max_length=30, null=True, blank=True, verbose_name="省份")
    local_city = models.CharField(max_length=30, null=True, blank=True, verbose_name="城市")
    local_district = models.CharField(max_length=30, null=True, blank=True, verbose_name="地区")
    is_boss = models.BooleanField(verbose_name="总教研员", default=False)


class EthereumQuesProScore(models.Model):
    """
        存以太坊的打分数据
    """
    question = models.ForeignKey('CompetitionQuestion', verbose_name="题目")
    production = models.ForeignKey('Production', verbose_name="作品")
    rater = models.ForeignKey('Teacher', verbose_name="评委")
    score_time = models.DateTimeField(verbose_name="评分时间")
    hash = models.CharField(verbose_name="哈希值", max_length=100)


class DownloadSource(models.Model):
    """
    下载资源模型
    """
    # gallery_production = models.ManyToManyField('Production', null=True, blank=True,through='galleryproduction')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='文件名称')
    uploader = models.ForeignKey(BaseUser, null=True, verbose_name='文件上传者')
    description = models.TextField(verbose_name="文件介绍", blank=True, null=True)
    fileUrl = models.CharField(verbose_name="资源下载链接", max_length=500)
    is_active = models.BooleanField(default=True,verbose_name='文件发布状态')


    def __unicode__(self):
        return self.uploader.username + '上传的' + self.name

    def __str__(self):
        return self.uploader.username + '上传的' + self.name

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


class dataVisualization(models.Model):
    """
    下载资源模型
    """
    # gallery_production = models.ManyToManyField('Production', null=True, blank=True,through='galleryproduction')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500, verbose_name='总图表名称')
    create_time = models.DateTimeField(verbose_name="创建时间", default=timezone.now)
    uploader = models.ForeignKey(BaseUser, null=True, verbose_name='编辑者')
    description = models.TextField(verbose_name="总图表介绍", blank=True, default='无')
    fileUrl = models.CharField(verbose_name="总图表链接", max_length=500,default='无')
    is_active = models.BooleanField(default=True, verbose_name='总图表发布状态')

    chartTitle1 = models.CharField(max_length=50, verbose_name='图表1标题',default='一、竞赛概况')
    chartAnalysisTitle1 = models.CharField(max_length=50, verbose_name='图表1分析标题',default='竞赛分析')
    chartAnalysisDescription1 = models.TextField(verbose_name="图表1分析描述", blank=True, null=True,default='暂无')
    chartFileUrl1 = models.CharField(verbose_name="图表1嵌入链接", max_length=500)

    chartTitle2 = models.CharField(max_length=50, verbose_name='图表2标题', default='二、参赛学生')
    chartAnalysisTitle2 = models.CharField(max_length=50, verbose_name='图表2分析标题', default='人群分析')
    chartAnalysisDescription2 = models.TextField(verbose_name="图表2分析描述", blank=True, null=True, default='暂无')
    chartFileUrl2 = models.CharField(verbose_name="图表2嵌入链接", max_length=500)


    chartTitle3 = models.CharField(max_length=50, verbose_name='图表3标题', default='三、参赛作品')
    chartAnalysisTitle3 = models.CharField(max_length=50, verbose_name='图表3分析标题', default='作品分析')
    chartAnalysisDescription3 = models.TextField(verbose_name="图表3分析描述", blank=True, null=True, default='暂无')
    chartFileUrl3 = models.CharField(verbose_name="图表3嵌入链接", max_length=500)

    chartTitle4 = models.CharField(max_length=50, verbose_name='图表4标题', default='四、评委打分')
    chartAnalysisTitle4 = models.CharField(max_length=50, verbose_name='图表4分析标题', default='打分分析')
    chartAnalysisDescription4 = models.TextField(verbose_name="图表4分析描述", blank=True, null=True, default='暂无')
    chartFileUrl4 = models.CharField(verbose_name="图表4嵌入链接", max_length=500)




    def __unicode__(self):
        return self.uploader.username + '发布的' + self.name

    def __str__(self):
        return self.uploader.username + '发布的' + self.name

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


class FormatSchool(models.Model):
    """
    废弃旧School表，移用此表为新表
    """
    name = models.CharField(verbose_name="学校名称", max_length=20)
    province = models.CharField(verbose_name="省份", max_length=10)
    city = models.CharField(verbose_name="城市", max_length=10)
    district = models.CharField(verbose_name="地区", max_length=20)
    chief = models.ForeignKey('Teacher', verbose_name="学校负责人")
    add_time = models.DateTimeField(verbose_name="添加时间", auto_now_add=True)
    is_active = models.BooleanField(verbose_name="是否激活", default=False)

    class Meta:
        #省份、城市、地区、名称四个字段联合唯一
        unique_together = (("province", "city", "district", "name"), )

    def __str__(self):
        return self.name


class FormatClass(models.Model):
    """
    废弃旧Class表，移用此表为新表
    """
    format_school = models.ForeignKey('FormatSchool', verbose_name="所属学校")
    #年级字段，从1-6中选择，毕业班级以当年毕业年份为年级号，兴趣班以组建的年份为年级号
    grade = models.IntegerField(verbose_name="年级")
    class_num = models.IntegerField(verbose_name="班级")
    chief = models.ForeignKey('Teacher', verbose_name="班级负责人")
    #是否为兴趣班，默认为False
    is_interest = models.BooleanField(verbose_name="是否兴趣班", default=False)
    add_time = models.DateTimeField(verbose_name="添加时间", auto_now_add=True)
    is_active = models.BooleanField(verbose_name="是否激活", default=False)

    class Meta:
        unique_together = (("format_school", "grade", "class_num", "is_interest"), )

    def __str__(self):
        return str(self.format_school) + "的" + str(self.grade) + "年级" + str(self.class_num) + "班"

    def get_full_name(self):
        return str(self.grade) + "年级" + str(self.class_num) + "班"
