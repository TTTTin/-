# -*- coding:utf-8 -*-
import hashlib
import json

from django.core.files.storage import FileSystemStorage
from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

from ordered_model.models import OrderedModel
from jsonfield import JSONField

from OJ.storages import OverwriteStorage
from scratch_api.models import Teacher, User, FormatClass
from django.conf import settings
import os

from django.dispatch import receiver
from django.db.models.signals import post_delete

# TESTCASE_DIR = os.path.join(settings.BASE_DIR, 'test_case')
TESTCASE_DIR = '/test_case'
TestCase_FileStorage = OverwriteStorage(location=TESTCASE_DIR)


def get_input_test_path(instance, filename):
    """
    set upload path for input_test
    """
    return os.path.join(str(instance.problem.pk), str(instance.order) + '.in')


def get_output_test_path(instance, filename):
    """
    set upload path for output_test
    """
    return os.path.join(str(instance.problem.pk), str(instance.order) + '.out')


def generate_testcase_info(problem):
    conf_path = os.path.join(TESTCASE_DIR, str(problem.pk), 'info')
    qs = problem.testcase_set.all()
    test_case_info = {'test_case_number': qs.count(), 'spj': False, 'test_cases': {}}

    # handle each test case
    for obj in qs:
        obj_info = {}
        with open(os.path.join(TESTCASE_DIR, str(problem.pk), str(obj.order) + '.out'), 'r') as output_file:
            output_content = output_file.read()
            obj_info['output_md5'] = hashlib.md5(output_content.encode()).hexdigest()
            obj_info['stripped_output_md5'] = hashlib.md5(output_content.rstrip().encode()).hexdigest()
            obj_info['output_size'] = len(output_content)
            obj_info['output_name'] = str(obj.order) + '.out'
        with open(os.path.join(TESTCASE_DIR, str(problem.pk), str(obj.order) + '.in'), 'r') as input_file:
            input_content = input_file.read()
            obj_info['input_name'] = str(obj.order) + '.in'
            obj_info['input_size'] = len(input_content)
        test_case_info['test_cases'][str(obj.order)] = obj_info

    # write to file
    with open(conf_path, 'w') as f:
        f.write(json.dumps(test_case_info, indent=4))


class Problem(models.Model):
    # 问题表，储存问题信息
    LEVEL_CHOICES = (
        ('1', '简单'),
        ('2', '中等'),
        ('3', '困难'),
    )
    title = models.CharField(verbose_name='标题', max_length=50)
    # description = models.CharField(verbose_name='问题描述', max_length=200)
    description = RichTextUploadingField(verbose_name='问题描述')
    input_description = RichTextUploadingField(verbose_name='输入描述')
    output_description = RichTextUploadingField(verbose_name='输出描述')
    hint = models.CharField(verbose_name='提示', max_length=100, null=True, blank=True)
    PERMISSION_CHOICES = (
        ('PR', '私有的'),  # private
        ('MC', '我教的班级可以做题'),  # my class
        ('PB', '公开的')  # public
    )
    permission = models.CharField(verbose_name='问题权限', max_length=2, choices=PERMISSION_CHOICES, default='MC',
                                  db_index=True)
    author = models.ForeignKey(Teacher, verbose_name='作者')
    classes = models.ManyToManyField(FormatClass, blank=True, verbose_name="可见班级")
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='题目更新时间', auto_now=True)
    time_limit = models.IntegerField(verbose_name='时间限制（ms）', default=1000)
    memory_limit = models.IntegerField(verbose_name='内存限制（kb）', default=256000)
    submission_number = models.IntegerField(verbose_name='总提交次数', default=0)
    accepted_number = models.IntegerField(verbose_name='AC数', default=0)
    ACrate = models.FloatField(verbose_name="通过率", editable=False)
    level = models.CharField(verbose_name='难度', choices=LEVEL_CHOICES, default='1', max_length=10)
    tags = models.ManyToManyField('Tag', verbose_name='标签', blank=True, max_length=10)

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.ACrate = self.accepted_number / self.submission_number if self.submission_number else 0
        if self.permission != 'MC' and Problem.objects.filter(id=self.id).count() != 0:
            self.classes.clear()
        super(Problem, self).save(*args, **kwargs)


class TestCase(OrderedModel):
    problem = models.ForeignKey(Problem, verbose_name='所属问题')
    order = models.PositiveIntegerField(editable=False, db_index=True, verbose_name="测试编号")
    input_test = models.FileField(upload_to=get_input_test_path, storage=TestCase_FileStorage, verbose_name='输入')
    output_test = models.FileField(upload_to=get_output_test_path, storage=TestCase_FileStorage, verbose_name='输出')
    order_with_respect_to = 'problem'

    def __str__(self):
        return self.problem.title + " " + str(self.order)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        generate_testcase_info(self.problem)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


""" 在TestCase删除一个model后执行的操作：删除服务器上相应的文件和更新info文件"""


@receiver(post_delete, sender=TestCase)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    # if instance.input_test:
    #     if os.path.isfile(instance.input_test.path):
    #         os.remove(instance.input_test.path)
    # print('自定义auto_delete_file_on_delete')
    instance.input_test.delete(False)
    instance.output_test.delete(False)
    generate_testcase_info(instance.problem)


class Tag(models.Model):
    name = models.CharField(verbose_name='名称', max_length=10)
    count = models.IntegerField(verbose_name='引用次数', default=0)

    def __str__(self):
        return self.name


class JudgeStatus:
    COMPILE_ERROR = -2
    WRONG_ANSWER = -1
    ACCEPTED = 0
    CPU_TIME_LIMIT_EXCEEDED = 1
    REAL_TIME_LIMIT_EXCEEDED = 2
    MEMORY_LIMIT_EXCEEDED = 3
    RUNTIME_ERROR = 4
    SYSTEM_ERROR = 5
    PENDING = 6
    PARTIALLY_ACCEPTED = 7


JudgeStatus2Chinese = {
    -2: "编译错误",
    -1: "答案错误",
    0: "正确",
    1: "超时错误",
    2: "超时错误",
    3: "内存超出错误",
    4: "运行时错误",
    5: "系统错误",
    6: "等待中",
    7: "部分正确"
}


class Submission(models.Model):
    problem = models.ForeignKey(Problem, verbose_name="所属问题")
    user = models.ForeignKey(User, verbose_name="提交用户")
    submission_time = models.DateTimeField(auto_now_add=True)
    code = models.TextField(verbose_name="提交代码")
    result = models.IntegerField(default=JudgeStatus.PENDING)
    info = JSONField(blank=True)
    language = models.CharField(max_length=20)

    @property
    def result_zh(self):
        return JudgeStatus2Chinese[self.result]


class SubmissionDailystatistical(models.Model):
    user = models.ForeignKey(User, verbose_name='提交用户')
    submission_day = models.DateField(auto_now=False, auto_now_add=False, verbose_name='提交日期')
    submission_count = models.IntegerField(default=0, verbose_name="提交记录数")

    def __str__(self):
        return self.user.baseuser_ptr_id + '/' + str(self.submission_day)
