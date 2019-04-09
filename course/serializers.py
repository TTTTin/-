from rest_framework import serializers
from course.models import Lesson, Chapter


class LessonSerializer(serializers.ModelSerializer):
    TOC = serializers.SerializerMethodField()
    class Meta:
        model = Lesson
        fields = ['lesson_id', 'name', 'author', 'audio', 'image', 'short_introduction','task', 'TOC']
        ordering = ('lesson_id', )

    def get_TOC(self, obj):
        lesson_id = obj.lesson_id
        try:
            lesson_obj = Lesson.objects.get(lesson_id=lesson_id)
        except Exception as e:
            return None
        TOC = Chapter.objects.filter(lesson_id=lesson_obj).values('chapter_id', 'name').order_by("chapter_id")
        return TOC


class ChapterSerializer(serializers.ModelSerializer):

    previous = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()

    def get_previous(self, obj):
        lesson_id = obj.lesson_id
        chapter_id = obj.chapter_id
        chapter = Chapter.objects.filter(lesson=lesson_id, chapter_id=obj.chapter_id - 1)
        if chapter:
            return '/' + str(lesson_id) + '/' + str(chapter_id - 1)
        else:
            return None

    def get_next(self, obj):
        lesson_id = obj.lesson_id
        chapter_id = obj.chapter_id
        chapter = Chapter.objects.filter(lesson=lesson_id, chapter_id=obj.chapter_id + 1)
        if chapter:
            return '/' + str(lesson_id) + '/' + str(chapter_id + 1)
        else:
            return None


    class Meta:
        model = Chapter
        fields = ['lesson', 'chapter_id', 'name', 'audio', 'create_time', 'update_time', 'previous',
                  'next']
