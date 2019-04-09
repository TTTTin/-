from django_tables2 import tables
from django_tables2.utils import A
from OJ.models import Problem, Submission


class ProblemTable(tables.Table):
    isAC = tables.columns.BooleanColumn(verbose_name="", empty_values=(), attrs={
        'td': {
            'width': 5
        }})
    id = tables.columns.Column(verbose_name="#")
    title = tables.columns.LinkColumn('OJ:problem_detail', args=[A('pk')])
    ACrate = tables.columns.Column()
    author = tables.columns.Column()
    level = tables.columns.Column()


    def render_ACrate(self, value):
        return "%.2f%%" %(value*100)

    def render_isAC(self, record):
        if self.user.is_anonymous():
            return '✘'
        if Submission.objects.filter(problem=record.pk, user=self.user, result=0).exists():
            return '✔'
        elif Submission.objects.filter(problem=record.pk, user=self.user).exists():
            return '?'
        else:
            return '✘'

    class Meta:
        # django tables2用了model后自定义Column就失效，所以这里不能使用model，要手动写所有的Column
        template_name = 'django_tables2/bootstrap.html'
        sequence = ('isAC', 'id', 'title', 'author', 'ACrate', 'level')
