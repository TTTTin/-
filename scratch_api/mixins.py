from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from course.models import Lesson
from scratch_api.models import Competition,CompetitionUser,User
from OJ.models import Problem


class CourseAuthorRequiredMixin(LoginRequiredMixin):
    """
    CBV mixin which verifies that the user is course author.
    """
    def dispatch(self, request, *args, **kwargs):
        try:
            lesson_id = self.kwargs.get("lesson")
            lesson = Lesson.objects.get(lesson_id=lesson_id)
            print(request.user)
        except Exception:
            return HttpResponseRedirect("/t/course_management/")
        if request.user.pk == lesson.author.pk:
            return super(CourseAuthorRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/t/course_management/")

class CompetitionAuthorRequiredMixin(LoginRequiredMixin):
    """
    CBV mixin which verifies that the user is course author.
    """
    def dispatch(self, request, *args, **kwargs):
        try:
            com_pk = self.kwargs.get("pk")
            competition = Competition.objects.get(pk=com_pk)
            print(request.user)
        except Exception:
            return HttpResponseRedirect("/t/competition_management_admin/")
        if request.user.pk == competition.creator.pk:
            return super(CompetitionAuthorRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/t/competition_management_admin/")


class CompetitionUserAuthorRequiredMixin(LoginRequiredMixin):
    """
    CBV mixin which verifies that the user is course author.
    """
    def dispatch(self, request, *args, **kwargs):
        # try:
            com_pk = self.kwargs.get("user")
            print(com_pk)
            competition_user = User.objects.get(username=com_pk)
            user = CompetitionUser.objects.get(user=competition_user)
            print(request.user)
            return super(CompetitionUserAuthorRequiredMixin, self).dispatch(request, *args, **kwargs)
        # except Exception:
        #     print("111")
        #     return HttpResponseRedirect("/t/compro_management_user/")
        # if request.user.pk == competition.creator.pk:
        #     return super(CompetitionUserAuthorRequiredMixin, self).dispatch(request, *args, **kwargs)
        # else:
        #     return HttpResponseRedirect("/t/compro_management_user/")

class ProblemAuthorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            problem_id = self.kwargs.get("problem")
            problem = Problem.objects.get(id=problem_id)
            print(request.user)
        except Exception:
            return HttpResponseRedirect("/t/problem_management/")
        if request.user.pk == problem.author.pk:
            return super(ProblemAuthorRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/t/problem_management/")
