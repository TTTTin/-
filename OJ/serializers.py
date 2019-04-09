from rest_framework import serializers

from OJ.models import Submission


class SubmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Submission
        fields = ('problem', 'user', 'code', 'language')


class ProblemSubmissionHistorySerializer(serializers.ModelSerializer):
    result = serializers.CharField(source='result_zh')

    class Meta:
        model = Submission
        fields = ('id', 'submission_time', 'result', 'info', 'language')