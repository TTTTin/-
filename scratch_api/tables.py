# encoding=utf-8
from __future__ import unicode_literals,absolute_import
import django_tables2 as tables
from django.db.models import F
from notifications.models import Notification

from scratch_api.models import User, Teacher,Competition, CompetitionQuestion,ANTLRScore,CompetitionUser
from .models import Production, Class,TeacherScore, FormatClass
from course.models import Lesson
from course.models import Chapter
from OJ.models import Problem


from django.utils.safestring import mark_safe

from django_tables2.utils import Accessor, AttributeDict

from django_tables2.utils import A



class ProdcutionTable(tables.Table):
    url = tables.TemplateColumn('<a onclick="return ViewCall(this);" href="/t/production/{{record.id}}">打分</a>', verbose_name='操作', orderable=False)
    student = tables.Column(accessor='author.name', verbose_name='作者')
    imgelink = tables.TemplateColumn(
        '<a href="/productdetail/{{record.id}}"><img height="200" width="200" src="/media/{{record.image}}" \></a>', verbose_name='作品详情')

    class Meta:
        attrs = {'class': 'footable table table-stripped',
                 'th': {
                     'onclick': "return SortCall(this)",
                     # 'onclick': "return SortCall(this)",
                     # 修改这里为你需要click的函数
                 },
                 'td': {
                     "style": "vertical-align: middle !important"
                 }

                 }
        model = Production
        fields = ['imgelink', 'name', 'student','lesson','comment_eachother_all_score', 'teacherscore.score', 'create_time','update_time', 'url']

class ProdcutionGradeTable(tables.Table):
    url = tables.TemplateColumn('<a onclick="return ViewCall(this);" href="/t/production/{{record.id}}">查看</a>', verbose_name='操作', orderable=False)
    student = tables.Column(accessor='author.name', verbose_name='作者')
    imgelink = tables.TemplateColumn(
        '<a href="/productdetail/{{record.id}}"><img height="200" width="200" src="/media/{{record.image}}" \></a>', verbose_name='作品详情')

    class Meta:
        attrs = {'class': 'footable table table-stripped',
                 'th': {
                     'onclick': "return SortCall(this)",
                     # 'onclick': "return SortCall(this)",
                     # 修改这里为你需要click的函数
                 },
                 'td': {
                     "style": "vertical-align: middle !important"
                 }

                 }
        model = Production
        fields = ['imgelink','name', 'student','lesson','comment_eachother_all_score','teacherscore.score','create_time', 'update_time', 'url']


class ProdcutionDownloadTable(tables.Table):
    grade = tables.TemplateColumn('<a onclick="return ViewCall(this);" href="/t/production/{{record.id}}">打分</a>', verbose_name='打分', orderable=False)
    url = tables.TemplateColumn('<a href="{{record.file.url}}">下载</a>', verbose_name='下载', orderable=False)
    imgelink = tables.TemplateColumn(
        '<a href="/productdetail/{{record.id}}"><img height="200" width="200" src="/media/{{record.image}}" \></a>',
        verbose_name='作品详情', orderable=False)
    teacherscore = tables.Column(verbose_name="教师评分")

    def render_author(self, value):
        return value.name

    def render_teacherscore(self, value):
        if value:
            return int(value.score)
        return None

    def order_teacherscore(self, QuerySet, is_descending):
        QuerySet = QuerySet.order_by(("-" if is_descending else '') + "teacherscore__score")
        return (QuerySet, True)

    class Meta:
        attrs = {'class': 'footable table table-stripped',
                 'td': {
                     "style": "vertical-align: middle !important"
                 }
                }
        model = Production
        fields = ['imgelink', 'name', 'author', 'lesson', 'comment_eachother_all_score', 'teacherscore', 'create_time', 'update_time', 'url']


class EProdcutionTable(tables.Table):
    url = tables.TemplateColumn('<a onclick="return ViewCall(this);" href="/exam/production/{{record.id}}">查看</a>', verbose_name='操作', orderable=False)
    student = tables.Column(accessor='author.name', verbose_name='作者')

    class Meta:
        attrs = {'class': 'footable table table-stripped',
                 'th': {
                     'onclick': "return SortCall(this)",
                     # 'onclick': "return SortCall(this)",
                     # 修改这里为你需要click的函数
                 }

                 }
        model = Production
        fields = ['name', 'student','lesson','comment_eachother_all_score','create_time', 'update_time', 'url']
# class ClassTable(tables.Table):
#     school_name = tables.Column(verbose_name='学校')
#     class_name = tables.Column(verbose_name='班级')
#     code = tables.Column(verbose_name='班级编号')
#     url1 = tables.TemplateColumn('<a href="{{record.id}}/">查看班级</a>', verbose_name='操作', orderable=False)
#     url2 = tables.TemplateColumn('<a href="/t/class_management/{{record.id}}/delete">删除班级</a>', verbose_name='操作', orderable=False)
#     # print({{record}})
#     class Meta:
#         attrs = {'class': 'footable table table-stripped'}
#         model = Class
#         fields = ['school_name', 'class_name','code']


class ClassTable(tables.Table):
    format_school = tables.Column(verbose_name='学校')
    grade = tables.Column(verbose_name='年级')
    class_num = tables.Column(verbose_name='班级')
    # chief = tables.Column(verbose_name='班级负责人')
    is_interest = tables.Column(verbose_name='是否为兴趣班')
    url1 = tables.TemplateColumn('<a href="/t/class_management/{{record.id}}/">查看班级</a>', verbose_name='操作', orderable=False)
    # url3 = tables.TemplateColumn('<a href="/t/class_management_add/{{record.id}}/">添加学生</a>', verbose_name='操作', orderable=False)
    url2 = tables.TemplateColumn('<a href="/t/class_management/{{record.id}}/delete">删除班级</a>', verbose_name='操作', orderable=False)
    # print({{record}})

    class Meta:
        attrs = {'class': 'footable table table-stripped'}
        model = FormatClass
        fields = ['format_school', 'grade', 'class_num', 'is_interest']


class CourseTable(tables.Table):
    lesson_id = tables.Column(verbose_name='课程编号')
    name = tables.Column(verbose_name='课程名称')
    short_introduction = tables.Column(verbose_name='简短介绍')
    print("{{record.name}}")
    url1 = tables.TemplateColumn('<a href="/t/course_management/{{record.lesson_id}}/">查看课程</a>', verbose_name='操作', orderable=False)
    url2 = tables.TemplateColumn('<a href="/t/course_management/{{record.lesson_id}}/delete/">删除课程</a>', verbose_name='操作', orderable=False)
    url3 = tables.TemplateColumn('<a href="/t/chapter_management/{{record.lesson_id}}/?sort=order">章节管理</a>', verbose_name='操作', orderable=False)

    class Meta:
        attrs = {'class': 'footable table table-stripped'}
        model = Lesson
        fields = ['lesson_id', 'name', 'short_introduction']

class TeacherTable(tables.Table):
    school_name = tables.Column(verbose_name='学校')
    class_name = tables.Column(verbose_name='班级')
    code = tables.Column(verbose_name='班级编号')
    url1 = tables.TemplateColumn('<a href="{{record.id}}/">查看班级</a>', verbose_name='操作', orderable=False)
    url2 = tables.TemplateColumn('<a href="/t/class_management/{{record.id}}/delete">删除班级</a>', verbose_name='操作', orderable=False)
    # print({{record}})
    class Meta:
        attrs = {'class': 'footable table table-stripped'}
        model = Class
        fields = ['school_name', 'class_name','code']

class ChapterTable(tables.Table):
    # chapter_id = tables.Column(verbose_name='章节编号')
    order = tables.Column(verbose_name='章节编号')
    name = tables.Column(verbose_name='章节名称')
    create_time = tables.Column(verbose_name='创建时间')
    update_time = tables.Column(verbose_name='更新时间')

    url1 = tables.TemplateColumn('<a href="/t/chapter_management/{{record.lesson.lesson_id}}/{{record.chapter_id}}/">查看章节</a>', verbose_name='操作', orderable=False)
    url2 = tables.TemplateColumn('<a href="/t/chapter_management/{{record.lesson.lesson_id}}/{{record.chapter_id}}/delete/">删除章节</a>', verbose_name='操作', orderable=False)
    url3 = tables.TemplateColumn('<a href="javascript:" id="up" class="up"><img width="24px" height="24px" src="/../static/img/up1.png"></a>',verbose_name='操作', orderable=False)
    url4 = tables.TemplateColumn('<a href="#" id="down" class="down"><img width="24px" height="24px" src="/../static/img/down1.png"></a>',verbose_name='操作', orderable=False)
    # url5 = tables.TemplateColumn('<a href="#" id="top" class="top"><img width="auto" height="12%" src="/../static/img/top.png"></a>',verbose_name='操作', orderable=False)

    class Meta:
        attrs = {'class': 'footable table table-stripped'}
        model = Chapter
        fields = ['order', 'name', 'create_time', 'update_time']


# class UserTable(tables.Table):
#
#     username = tables.Column(verbose_name='用户名')
#     name = tables.Column(verbose_name="真实姓名")
#     sex = tables.Column(verbose_name="性别")
#     url_info = tables.TemplateColumn('<a class="url_info" href="/t/update_student/{{record.pk}}/">修改信息</a>', verbose_name='操作', orderable=False)
#     url_password = tables.TemplateColumn('<a class="url_password" href="/t/reset_student_password/{{record.pk}}/">重设密码</a>',verbose_name='操作', orderable=False)
#     # delete_student = tables.TemplateColumn('<a class="delete_student" href="/t/delete_class_student/{{record.pk}}/">删除学生</a>',verbose_name='操作', orderable=False)
#     delete_student = tables.TemplateColumn('<a class="delete_student" href="javascript:void(0)" onclick="deletestu('"'{{record.pk}}'"')">解除班级关系</a>',verbose_name='操作', orderable=False)
#     checkbox = tables.TemplateColumn('<input type="checkbox" name="message" value="{{ record.pk }}" />', verbose_name="选择", orderable=False)
#     class Meta:
#         attrs = {'class': 'footable table table-stripped '}
#         model = User
#         fields = ['username', 'name', 'sex','url_info', 'url_password','delete_student','checkbox']
#         # fields = ['username', 'name', 'sex','url_info', 'url_password','delete_student']


class UserTable(tables.Table):

    username = tables.Column(verbose_name='用户名')
    name = tables.Column(verbose_name="真实姓名")
    sex = tables.Column(verbose_name="性别")
    url_info = tables.TemplateColumn('<a class="url_info" href="javascript:void(0)" onclick="updatestu('"'{{record.pk}}'"')">修改信息</a>', verbose_name='操作', orderable=False)
    url_password = tables.TemplateColumn('<a class="url_password" href="/t/reset_student_password/{{record.pk}}/">重设密码</a>',verbose_name='操作', orderable=False)
    # delete_student = tables.TemplateColumn('<a class="delete_student" href="/t/delete_class_student/{{record.pk}}/">删除学生</a>',verbose_name='操作', orderable=False)
    delete_student = tables.TemplateColumn('<a class="delete_student" href="javascript:void(0)" onclick="deletestu('"'{{record.pk}}'"')">解除班级关系</a>',verbose_name='操作', orderable=False)
    checkbox = tables.TemplateColumn('<input type="checkbox" name="message" value="{{ record.pk }}" />', verbose_name="选择", orderable=False)
    class Meta:
        attrs = {'class': 'footable table table-stripped '}
        model = User
        fields = ['username', 'name', 'sex']
        # fields = ['username', 'name', 'sex','url_info', 'url_password','delete_student']


class UserListTable(tables.Table):

    username = tables.Column(verbose_name='用户名')
    name = tables.Column(verbose_name="真实姓名")
    sex = tables.Column(verbose_name="性别")
    format_school = tables.Column(verbose_name="所属学校")
    # format_class = tables.ManyToManyColumn(transform=lambda format_class: format_class.get_full_name())
    # format_class1 = tables.Column(verbose_name="所属班级")
    # school=tables.Column(verbose_name="学校")
    # class1= tables.Column(verbose_name="班级")
    url_info = tables.TemplateColumn('<a class="url_info" href="/t/update_student_all/{{record.pk}}/">修改信息</a>', verbose_name='操作', orderable=False)
    url_password = tables.TemplateColumn('<a class="url_password" href="/t/reset_student_password/{{record.pk}}/">重设密码</a>', verbose_name='操作', orderable=False)
    delete_student = tables.TemplateColumn('<a class="delete_student" href="/t/alldelete_class_student/{{record.pk}}/">删除学生</a>',verbose_name='操作', orderable=False)
    # delete_student = tables.TemplateColumn('<a class="delete_student" href="javascript:void(0)" onclick="alldeletestu('"'{{record.pk}}'"')">删除学生</a>',verbose_name='操作', orderable=False)
    # checkbox = tables.TemplateColumn('<input type="checkbox" name="message" value="{{ record.pk }}" />', verbose_name="选择", orderable=False)

    # def render_format_class(self, value):
    #     return value

    class Meta:
        attrs = {'class': 'footable table table-stripped '}
        model = User
        fields = ['username', 'name', 'sex', 'format_school', 'format_class', 'url_info', 'url_password', 'delete_student']
        # fields = ['username', 'name', 'sex','url_info', 'url_password','delete_student']


class ClassAddUserTable(tables.Table):
    username = tables.Column(verbose_name='用户名')
    name = tables.Column(verbose_name="真实姓名")
    sex = tables.Column(verbose_name="性别")
    checkbox = tables.TemplateColumn('<input type="checkbox" name="message" value="{{ record.pk }}" />', verbose_name="选择", orderable=False)

    class Meta:
        attrs = {'class': 'footable table table-stripped '}
        model = User
        fields = ['username', 'name', 'sex']


class TeacherTable(tables.Table):
    username = tables.Column(verbose_name='用户名')
    name = tables.Column(verbose_name='姓名')
    format_school = tables.Column(verbose_name="所属学校")
    manage_permission = tables.TemplateColumn('<a class="manage_permission" href="/t/change_teacher_permission/?user={{record.username}}">修改职位</a>', verbose_name='修改职位', orderable=False)

    class Meta:
        attrs = {'class': 'footable table table-stripped '}
        model = Teacher
        fields = ['username', 'name', 'format_school', 'manage_permission']
# 竞赛表
class CompetitionTable(tables.Table):
    id=tables.Column(verbose_name='竞赛编号',accessor='pk')
    title = tables.Column(verbose_name='竞赛名称')
    creator = tables.Column(verbose_name="创建者")
    start_time = tables.Column(verbose_name="开始时间")
    stop_time = tables.Column(verbose_name="结束时间")
    content = tables.TemplateColumn('<a href="../../files/{{record.content}}">评分说明</a>', verbose_name='操作', orderable=False)

    # content = tables.TemplateColumn('<button onclick="window.open(/media/{{record.content}})"> 模版下载 </button>',
    #                                 verbose_name='操作', orderable=False)
    url1 = tables.TemplateColumn('<a href="/t/compro_management/{{record.pk}}/">查看作品</a>', verbose_name='操作', orderable=False)

    class Meta:
        attrs = {'class': 'footable table table-stripped'}
        model = Competition
        fields = ['id','title', 'creator','start_time','stop_time','content']

class CompetitionAdviserTable(tables.Table):
    id=tables.Column(verbose_name='竞赛编号',accessor='pk')
    title = tables.Column(verbose_name='竞赛名称')
    creator = tables.Column(verbose_name="创建者")
    start_time = tables.Column(verbose_name="开始时间")
    stop_time = tables.Column(verbose_name="结束时间")
    url1 = tables.TemplateColumn('<a href="/t/compro_management_adviser/{{record.pk}}/">查看作品</a>', verbose_name='操作',
                                 orderable=False)
    url2 = tables.TemplateColumn('<a href="/t/compro_progress/{{record.pk}}/">查看打分进展</a>', verbose_name='操作',
                                 orderable=False)
    url3 = tables.TemplateColumn('<a href="/t/compro_score_final/{{record.pk}}/">查看成绩</a>', verbose_name='操作',
                                 orderable=False)

    class Meta:
        attrs = {'class': 'footable table table-stripped'}
        model = Competition
        fields = ['id','title', 'creator','start_time','stop_time']


class CompetitionAdminTable(tables.Table):
    id=tables.Column(verbose_name='竞赛编号',accessor='pk')
    title = tables.Column(verbose_name='竞赛名称')
    creator = tables.Column(verbose_name="创建者")
    start_time = tables.Column(verbose_name="开始时间")
    stop_time = tables.Column(verbose_name="结束时间")
    # content = tables.TemplateColumn('<a href="{{record.file.url}}">竞赛内容</a>', verbose_name='操作', orderable=False)
    url1 = tables.TemplateColumn('<a href="/t/competition_management_admin/{{record.pk}}/">查看竞赛</a>', verbose_name='操作',
                                 orderable=False)
    url2 = tables.TemplateColumn('<a href="/t/competition_management/{{record.pk}}/delete/">删除竞赛</a>',
                                 verbose_name='操作', orderable=False)
    url3 = tables.TemplateColumn('<a href="/t/compro_management_admin/{{record.pk}}/">查看作品</a>', verbose_name='操作',
                                 orderable=False)
    url4 = tables.TemplateColumn('<a href="/t/compro_management_user/{{record.pk}}/">查看参赛者</a>', verbose_name='操作',
                                 orderable=False)
    # url5 = tables.TemplateColumn('<a href="/t/export_score/{{record.pk}}/">导出成绩</a>', verbose_name='操作',
    #                              orderable=False)
    class Meta:
        attrs = {'class': 'footable table table-stripped'}
        model = Competition
        fields = ['id','title', 'creator','start_time','stop_time']

class ComUserTable(tables.Table):
    competition=tables.Column(verbose_name="竞赛")
    user=tables.Column(verbose_name="参赛者")
    tutor=tables.Column(verbose_name="指导老师")
    delay_time=tables.Column(verbose_name="延迟时间")
    url1 = tables.TemplateColumn('<a href="/t/compro_management_user_update/{{record.competition.id}}/{{record.user}}/">修改延时</a>',verbose_name='操作', orderable=False)
    class Meta:
        attrs = {'class': 'footable table table-stripped'}
        model = CompetitionUser
        fields = ['competition','user', 'tutor','delay_time']

class ComProTable(tables.Table):
    question = tables.Column(verbose_name="题目")
    id = tables.Column(verbose_name='作品编号')
    # competition = tables.Column( verbose_name="所属竞赛")
    production = tables.Column(verbose_name="作品")
    create_time = tables.Column(verbose_name="创建时间")
    ct_score = tables.Column(verbose_name="CT得分")
    # limit_score=tables.Column(verbose_name="满分")
    score = tables.Column(verbose_name="评分")
    url1 = tables.TemplateColumn('<a href="/t/compro/{{record.question}}/{{record.id}}/">作品打分</a>', verbose_name='操作', orderable=False)

    class Meta:
        attrs = {'class': 'footable table table-stripped'}

class ComProAdminTable(tables.Table):
    name = tables.Column(verbose_name='作者')
    id = tables.Column(verbose_name='作品编号')
    question = tables.Column(verbose_name="题目")
    competition = tables.Column( verbose_name="所属竞赛")
    production = tables.Column(verbose_name="作品")
    create_time = tables.Column(verbose_name="创建时间")
    limit_score = tables.Column(verbose_name="满分")
    checkbox = tables.TemplateColumn('<input type="checkbox" name="message" value="{{ record.id }}" />',
                                     verbose_name="选择", orderable=False)

    class Meta:
        attrs = {'class': 'footable table table-stripped'}


class ComProAdviserTable(tables.Table):
    name = tables.Column(verbose_name='作者')
    id = tables.Column(verbose_name='作品编号')
    question = tables.Column(verbose_name="题目")
    production = tables.Column(verbose_name="作品")
    create_time = tables.Column(verbose_name="创建时间")
    ct_score = tables.Column(verbose_name="CT得分")
    avg_score = tables.Column(verbose_name="平均分")
    score = tables.Column(verbose_name="评分")

    url1 = tables.TemplateColumn('<a href="/t/compro_adviser/{{record.question}}/{{record.id}}/">作品打分</a>', verbose_name='操作',
                                 orderable=False)
    class Meta:
        attrs = {'class': 'footable table table-stripped'}


class ComProgressTable(tables.Table):
    rater = tables.Column(verbose_name="评委")
    question = tables.Column(verbose_name="题目")
    avg_score = tables.Column(verbose_name="平均分")  # 该题该评委评的所有平均分
    all_production = tables.Column(verbose_name="所有作品数")
    score_production = tables.Column(verbose_name="未评分作品数")

    class Meta:
        attrs = {'class': 'footable table table-stripped'}


class ComProScoreTable(tables.Table):
    school = tables.Column(verbose_name="学校")
    user = tables.Column(verbose_name="参赛者姓名")
    competition = tables.Column(verbose_name="所属竞赛")
    # question = tables.Column(verbose_name="题目")
    # production = tables.Column(verbose_name="作品")
    avg_score = tables.Column(verbose_name="平均分")  # N个评委的平均分
    ct_score = tables.Column(verbose_name="CT得分")
    total_score = tables.Column(verbose_name="总分")

    class Meta:
        attrs = {'class': 'footable table table-stripped'}


class ProblemTable(tables.Table):
    id = tables.Column(verbose_name='序号')
    title = tables.Column(verbose_name='题目名称')
    author = tables.Column(verbose_name='作者')
    create_time = tables.Column(verbose_name='创建时间')
    update_time = tables.Column(verbose_name='更新时间')
    url1 = tables.TemplateColumn('<a href="{{record.id}}">查看题目</a>', verbose_name='操作', orderable=False)
    url2 = tables.TemplateColumn('<a href="/OJ/problem_management/{{record.id}}/delete/">删除题目</a>',
                                 verbose_name='操作', orderable=False)
    url3 = tables.TemplateColumn('<a href="/OJ/test_cases_management/{{record.id}}">测试用例</a>',
                                 verbose_name='操作', orderable=False)
    class Meta:
        attrs = {'class': 'footable table table-stripped'}
        model = Problem
        fields = ['id', 'title', 'author', 'create_time', 'update_time']


class TestCasesTable(tables.Table):
    problem = tables.Column(verbose_name='所属问题')
    order = tables.Column(verbose_name='测试编号')
    input_test = tables.Column(verbose_name='输入')
    output_test = tables.Column(verbose_name='输出')
    url1 = tables.TemplateColumn('<a href="{{record.order}}">查看用例</a>', verbose_name='操作', orderable=False)
    url2 = tables.TemplateColumn('<a href="{{record.order}}/delete/">删除用例</a>', verbose_name='操作', orderable=False)


    class Meta:
        attrs = {'class': 'footable table table-stripped'}
        model = Problem
        fields = ['problem', 'order', 'input_test', 'output_test']


class ApplyTable(tables.Table):
    kind_name = tables.Column(verbose_name="类型")
    name = tables.Column(verbose_name="名称")
    is_interest = tables.Column(verbose_name="兴趣班")
    chief = tables.Column(verbose_name="申请者")
    checkbox = tables.TemplateColumn('<input type="checkbox" class="{{ record.kind }}" name="message" value="{{ record.pk }}" />',
                                     verbose_name="选择", orderable=False)

    class Meta:
        attrs = {'class': 'footable table table-stripped'}