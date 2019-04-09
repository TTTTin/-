from celery.result import AsyncResult
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from OJ.models import Submission, JudgeStatus2Chinese, SubmissionDailystatistical
from OJ.serializers import SubmissionSerializer, ProblemSubmissionHistorySerializer
from scratch_api.models import User
from .tasks import judge

import datetime


class SubmissionView(CreateAPIView):
    """
    Handle a new submission
    """
    model = Submission
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = SubmissionSerializer

    def post(self, request, *args, **kwargs):
        user = User.objects.get(username__exact=request.user)

        #记录每天的提交次数
        if SubmissionDailystatistical.objects.filter(user=user).exists():
            if (SubmissionDailystatistical.objects.filter(user=user, submission_day=datetime.date.today()).exists()):
                day_record = SubmissionDailystatistical.objects.get(user=user, submission_day=datetime.date.today())
                day_record.submission_count += 1
                day_record.save()
            else:
                day_record = SubmissionDailystatistical()
                day_record.user = user
                day_record.submission_day = datetime.date.today()
                day_record.submission_count = 1
                day_record.save()
        else:
            day_record = SubmissionDailystatistical()
            day_record.user = user
            day_record.submission_day = datetime.date.today()
            day_record.submission_count = 1
            day_record.save()

        data = request.data.copy()
        data['user'] = user
        serializer = SubmissionSerializer(data=data)
        if serializer.is_valid(raise_exception=False):
            submission = serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        task = judge.delay(submission.id)
        return Response(data={'submission_id': submission.id, 'task_id': task.id}, status=status.HTTP_201_CREATED)


class CheckView(APIView):
    """
    Check the status of a submission
    """
    def get(self, request):
        data = {}
        task_id = self.request.GET.get('task_id', None)
        submission_id = self.request.GET.get('submission_id', None)
        if task_id and submission_id:
            task_result = AsyncResult(task_id).status
            print("task_result", task_result)
            data['task_result'] = task_result
            if task_result == 'SUCCESS':
                submission = Submission.objects.get(pk=submission_id)
                data['submission_result'] = submission.result_zh
            elif task_result == 'FAILURE':
                submission = Submission.objects.get(pk=submission_id)
                data['submission_result'] = submission.result_zh
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)



class ProblemSubmissionHistoryListView(ListAPIView):
    """
    List a user's submissions of a problem
    """
    model = Submission
    serializer_class = ProblemSubmissionHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)
    ordering = ('submission_time',)

    def get_queryset(self):
        user = User.objects.get(username=self.request.user)
        problem = self.request.GET.get('problem', None)
        try:
            return Submission.objects.filter(user=user, problem = problem)
        except:
            return None

