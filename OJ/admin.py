from django.contrib import admin
from django.contrib.admin import AdminSite

from OJ.models import Problem, TestCase, Tag, Submission, SubmissionDailystatistical


# Register your models here.
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'pk', 'permission', 'author', 'create_time', 'update_time', 'submission_number',
                    'accepted_number']
    search_fields = ['title', 'author__username', ]
    filter_horizontal = ['classes', ]


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'problem', 'user', "result", "language"]
    search_fields = ['problem__title', 'user__name']

    class Meta:
        models = Submission


class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['pk', 'problem', 'order']
    search_fields = ['problem__title']

    class Meta:
        models = TestCase


class SubmissionDailystatisticalAdmin(admin.ModelAdmin):
    list_display = ['user', 'submission_day', 'submission_count']

    class Meta:
        models = SubmissionDailystatistical


admin.site.register(Problem, ProblemAdmin)
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(Tag)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(SubmissionDailystatistical,SubmissionDailystatisticalAdmin)


class OJAdminSite(AdminSite):
    site_header = "OJ管理系统"
    site_title = "OJ管理系统"
    index_title = "欢迎来到OJ管理系统"


oj_admin_site = OJAdminSite(name='OJ_admin')
oj_admin_site.register(Problem, ProblemAdmin)
oj_admin_site.register(TestCase, TestCaseAdmin)
oj_admin_site.register(Tag)
oj_admin_site.register(Submission, SubmissionAdmin)
oj_admin_site.register(SubmissionDailystatistical, SubmissionDailystatisticalAdmin)