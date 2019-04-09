from __future__ import unicode_literals
from ordered_model.models import OrderedModel
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from ckeditor.fields import RichTextField
from django.db.models import FileField, ImageField
from django.utils import six
from django.db.models import Max, Min, F
from scratch_api.models import Teacher, FormatClass
from scratch_api.models import User

def get_latest_lesson():
    try:
        id = Lesson.objects.latest('id').lesson_id + 1
    except Exception as e:
        id = 1
    return id


def get_latest_chapter(lesson):
    num = Chapter.objects.filter(lesson=lesson).count()
    return num + 1
    # try:
    #     id = Chapter.objects.latest('id').chapter_id + 1
    #
    # except Exception as e:
    #     id = 1
    # return id


class Lesson(models.Model):
    # 课程模型
    lesson_id = models.IntegerField(default=get_latest_lesson, verbose_name="课程编号", unique=True)
    name = models.CharField(max_length=50, verbose_name="课程名称", unique=True)
    author = models.ForeignKey(Teacher, null=True, blank=True, verbose_name="作者")
    classes = models.ManyToManyField(FormatClass, blank=True, verbose_name="可见班级")
    introduction = RichTextUploadingField(verbose_name="介绍")
    # tasks=models.TextField(blank=True, null=True, max_length=100, verbose_name="作业")
    task=RichTextUploadingField(verbose_name="作业")
    short_introduction = models.TextField(blank=True, null=True, max_length=100, verbose_name="简短介绍")
    audio = FileField(upload_to="course/", null=True, blank=True, verbose_name="音频")
    image = ImageField(upload_to="course/", default="course/nopic.jpg", verbose_name="课程图片")
    PERMISSION_CHOICES = (
        ('PR', '私有的'),#private
        ('MC', '我教的班级可以学习'),#my class
        ('PB', '公开的'),#public
    )
    permission = models.CharField(max_length=2, choices=PERMISSION_CHOICES, default='PR', verbose_name="课程权限",db_index=True)

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    def __str__(self):
        return str(self.lesson_id) + ' ' + self.name

    def save(self, *args, **kwargs):
        if self.permission != 'MC' and Lesson.objects.filter(id=self.id).count() != 0:
            self.classes.clear()
        super(Lesson, self).save(*args, **kwargs)


class Chapter(OrderedModel):
    # 章节模型
    lesson = models.ForeignKey(Lesson, verbose_name="课程")
    chapter_id = models.IntegerField(verbose_name="章节编号",db_index=True)
    # chapter_id = models.IntegerField(verbose_name="章节编号")
    name = models.CharField(max_length=50, verbose_name="章节名称",db_index=True)
    content = RichTextUploadingField(verbose_name="内容")
    audio = FileField(upload_to="course/", null=True, blank=True, verbose_name="音频")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间',db_index=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间',db_index=True)
    order_with_respect_to = 'lesson'

    class Meta:
        unique_together = (("lesson", "chapter_id"), ("lesson", "name"))

    def __str__(self):
        return self.lesson.name + "的" + self.name

    def save(self, *args, **kwargs):
        if getattr(self, self.order_field_name) is None:
            c = self.get_ordering_queryset().aggregate(Max(self.order_field_name)).get(self.order_field_name + '__max')
            setattr(self, self.order_field_name, 1 if c is None else c + 1)
        super().save(*args, **kwargs)

    def swap(self, qs):
        """
            Swap the positions of this object with a reference object.
        """
        try:
            replacement = qs[0]
        except IndexError:
            # already first/last
            return
        if not self._valid_ordering_reference(replacement):
            raise ValueError(
                "{0!r} can only be swapped with instances of {1!r} with equal {2!s} fields.".format(
                    self, self._get_class_for_ordering_queryset(),
                    ' and '.join(["'{}'".format(o[0]) for o in self._get_order_with_respect_to()])
                )
            )
        order, replacement_order = getattr(self, self.order_field_name), getattr(replacement, self.order_field_name)
        setattr(self, self.order_field_name, replacement_order)
        setattr(replacement, self.order_field_name, order)

        # 交换两个chapterid
        temp = replacement.chapter_id
        print(self.chapter_id, replacement.chapter_id)
        replacement.chapter_id = self.chapter_id
        self.chapter_id = -1
        print(self.chapter_id, replacement.chapter_id)
        self.save()
        replacement.save()

        self.chapter_id = temp
        self.save()


class UserBehaviorLesson(models.Model):
    # 用户行为模型
    # id = models.AutoField()
    user = models.CharField(max_length=50, verbose_name='作者')
    lesson_id = models.IntegerField(verbose_name='课程编号')
    chapter_id = models.IntegerField(verbose_name='章节编号')
    start_time = models.DateTimeField(verbose_name='进入课程时间')
    end_time = models.DateTimeField(verbose_name='离开课程时间')
    click_audio = models.BooleanField(verbose_name='是否点击语音')

    def __str__(self):
        return str(self.user) + "学习了第" + str(self.lesson_id) + "节课"

