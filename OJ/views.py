import django_filters
import time, json

import time as time
from django.shortcuts import render, HttpResponse
from django.views.generic import DetailView, View
from django_filters.views import FilterView
from django_tables2 import SingleTableView, SingleTableMixin

from OJ.forms import ProblemListSearchForm
from scratch_api.models import Teacher
from OJ.tables import ProblemTable
from .models import User, Problem, Tag, Submission, JudgeStatus, SubmissionDailystatistical, TestCase
from django.db.models import Q


class ProblemFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(queryset=Teacher.objects.filter(problem__isnull=False).distinct(),
                                              label="作者")
    tags = django_filters.ModelChoiceFilter(
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Problem
        fields = ['author', 'level', 'tags']


class Website_ProblemList(SingleTableMixin, FilterView):
    model = Problem
    table_class = ProblemTable
    template_name = "problem_list.html"
    paginate_by = 15
    filterset_class = ProblemFilter

    def get_queryset(self):
        # 这里我们需要改为按照权限获取能显示的题目
        # 老师：能看到公开的和自己出的；学生：能看到公开的和自己班级的
        if self.request.user.is_authenticated:
            try:
                if Teacher.objects.filter(username=self.request.user.username):
                    teacher = Teacher.objects.filter(username=self.request.user.username)
                    qs = Problem.objects.filter(Q(permission='PB') | Q(author=teacher))
                else:
                    user = User.objects.get(username=self.request.user.username)
                    user_classes = user.format_class.all()
                    qs = Problem.objects.none()
                    for one_class in user_classes:
                        qs = qs | Problem.objects.filter(permission='MC', classes=one_class)
                    qs = qs | Problem.objects.filter(permission='PB')

                search = self.request.GET.get("search", None)
                if search:
                    try:
                        search_qs = qs.filter(Q(title__contains=search) | Q(id=search))
                    except:
                        search_qs = qs.filter(Q(title__contains=search))
                    return search_qs
                else:
                    return qs
            except:
                pass
        else:
            qs = Problem.objects.none()
            return qs

        # search = self.request.GET.get("search", None)
        # if search:
        #     try:
        #         qs = Problem.objects.filter(Q(title__contains=search) | Q(id=search))
        #     except:
        #         qs = Problem.objects.filter(Q(title__contains=search))
        # else:
        #     qs = Problem.objects.all()
        # return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 我们这里把user传到table中
        context['table'].user = self.request.user
        search_form = ProblemListSearchForm(self.request.GET) if self.request.GET.get(
            "search") else ProblemListSearchForm()
        context['search_form'] = search_form
        problem_nums = Problem.objects.count()
        context['problem_nums'] = problem_nums
        if not self.request.user.is_anonymous():
            ac_submission = Submission.objects.filter(
                user=self.request.user.username,
                result=0
            ).values_list('problem', flat=True).distinct()
            ac_nums = ac_submission.count()
            context['ac_nums'] = ac_nums
        else:
            context['ac_nums'] = 0
        return context


class ProblemDetail(DetailView):
    model = Problem
    template_name = "problem_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = ProblemListSearchForm(self.request.GET) if self.request.GET.get(
            "search") else ProblemListSearchForm()
        context['search_form'] = search_form
        submission_id = self.request.GET.get("submission_id", "")
        if submission_id != "":
            submission = Submission.objects.get(id=submission_id)
            context['code'] = submission.code
            context['language'] = submission.language
        return context


class SubmissionDetail(DetailView):
    model = Submission
    template_name = "submission_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.result == -1:
            try:
                test_case = TestCase.objects.get(problem=self.object.problem, order=self.object.info['test_case'])
                input = test_case.input_test
                output = test_case.output_test
                with open(input.path) as f:
                    context['input'] = ''.join(f.readlines())
                with open(output.path) as f:
                    context['standardOutput'] = ''.join(f.readlines())
                context['userOutput'] = self.object.info['output'].rstrip()
            except:
                pass
        return context


class PersonalDetail(View):
    def get(self, request, username):
        print(username)
        user = User.objects.get(username=username)

        problem_all = Problem.objects.all().count()
        problem_sub_count = Submission.objects.filter(user=user).count()
        problem_solve = Submission.objects.filter(user=user, result=JudgeStatus.ACCEPTED).values(
            'problem').distinct().count()
        if (problem_sub_count == 0):
            problem_sub_success_count = 0
            accept_rate = 0
            datalist = [0, 1]
        else:
            problem_sub_success_count = Submission.objects.filter(user=user, result=JudgeStatus.ACCEPTED).count()
            accept_rate = round(problem_sub_success_count / problem_sub_count, 4) * 100
            datalist = [problem_sub_success_count, problem_sub_count - problem_sub_success_count]

        usrinfo = {
            'username': user,
            'problem_all': problem_all,
            'problem_solve': problem_solve,
            'problem_sub_count': problem_sub_count,
            'problem_sub_success_count': problem_sub_success_count,
            'accept_rate': accept_rate,
        }
        # print(usrinfo)
        # print(datalist)

        recent_sub_records = Submission.objects.filter(user=user).order_by('-submission_time')[:5]
        subitems = []
        for recent_record in recent_sub_records:
            problem_id = recent_record.problem.id
            problemName = recent_record.problem.title
            status = recent_record.result_zh
            time1 = recent_record.submission_time.strftime('%Y-%m-%d %H:%M:%S')
            tag = recent_record.language
            subitems.append({
                'problem_id': problem_id,
                'problemName': problemName,
                'status': status,
                'time': time1,
                'tag': tag,
            })
        # print(subitems)

        sub_records = SubmissionDailystatistical.objects.filter(user=user)
        hotmapdata = {}
        for record in sub_records:
            time_str = record.submission_day.strftime('%Y-%m-%d')
            time_array = time.strptime(str(time_str), "%Y-%m-%d")
            timestamp = int(time.mktime(time_array))
            hotmapdata[timestamp] = record.submission_count
        # print(hotmapdata)

        return render(request, "personal_detail.html", {
            'object': usrinfo,
            'subitems': subitems,
            'datalist': json.dumps(datalist),
            'hotmapdata': json.dumps(hotmapdata)
        })

        # 测试数据
        # usrinfo = {
        #     'username': 'pengcong',
        #     'problem_all': 800,
        #     'problem_solve': 20,
        #     'problem_sub_count': 500,
        #     'problem_sub_success_count': 400,
        #     'accept_rate': 80,
        # }
        #
        # datalist = [2, 8]
        # hotmapdata = {
        #     "86401": 1,
        #     "1526572800": 8,
        #     "1288411200": 8,
        #     "1288756800": 2,
        #     "1288929600": 10,
        #     "1289278800": 4
        # }
        # subitems = [
        #     {
        #         "problemName": '两数之和',
        #         "status": "编译出错",
        #         "time": "0",
        #         'tag': "cpp"
        #     },
        #     {
        #         "problemName": '两数之和',
        #         "status": "编译出错",
        #         "time": "0",
        #         'tag': "cpp"
        #     },
        #     {
        #         "problemName": '两数之和',
        #         "status": "编译出错",
        #         "time": "0",
        #         'tag': "cpp"
        #     }
        # ]
