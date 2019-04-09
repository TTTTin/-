from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from course.models import Lesson, Chapter
from scratch_api.models import Gallery


class GallerySerializer(serializers.ModelSerializer):

    image = serializers.ImageField()

    class Meta:
        model = Gallery
        fields = ['author', 'name', 'is_active', 'create_time', 'update_time', 'image', 'description']

    def validate(self, attrs):
        if Gallery.objects.filter(author__exact=attrs['author'], name__exact=attrs['name']).exists():
            raise ValidationError(detail={'code': '1', 'message': u'专题名重复'}, code=status.HTTP_409_CONFLICT)
        return attrs