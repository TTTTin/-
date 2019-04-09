# Register your models here.
from django.contrib import admin
from ckeditor.widgets import CKEditorWidget

from course.models import Lesson, Chapter, UserBehaviorLesson


class LessonAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'lesson_id', 'author', 'permission')

    class Meta:
        model = Lesson


class ChapterAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('lesson', 'chapter_id', 'name', 'order')
    list_filter = ('lesson',)

    class Meta:
        model = Chapter


class BehaviorAdmin(admin.ModelAdmin):
    search_fields = ('user',)
    list_display = ('lesson_id', 'chapter_id')
    #fields = ('user', 'lesson_id', 'chapter_id', 'start_time', 'end_time', 'click_audio')
    # exclude = []

    class Meta:
        model = UserBehaviorLesson


admin.site.register(Lesson, LessonAdmin)

admin.site.register(Chapter, ChapterAdmin)

admin.site.register(UserBehaviorLesson, BehaviorAdmin)
