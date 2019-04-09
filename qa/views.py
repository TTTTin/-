from django.http import Http404
from django.shortcuts import render

from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import FormMixin, UpdateView
from django.utils.translation import ugettext as _
from notifications.signals import notify

from qa.forms import QuestionForm, AnswerForm
from qa.mixins import AuthorRequiredMixin
from qa.models import Question, Answer


class QuestionIndexView(ListView):
    """CBV to render the index view
    """
    model = Question
    paginate_by = 20
    context_object_name = 'questions'
    template_name = 'qa/index.html'
    ordering = '-pub_date'
    queryset = Question.objects.all()


class CreateQuestionView(CreateView):
    """
    View to handle the creation of a new question
    """
    template_name = 'qa/create_question.html'
    message = '感谢!你的问题已经被成功创建'
    form_class = QuestionForm

    def form_valid(self, form):
        """
        Create the required relation
        """
        form.instance.user = self.request.user
        return super(CreateQuestionView, self).form_valid(form)

    def get_success_url(self):
        return reverse('qa:qa_index')


class QuestionDetailView(ListView, FormMixin):
    """
    View to call a question and to render all the details about that question.
    """
    model = Answer
    template_name = 'qa/detail_question.html'
    context_object_name = 'answers'
    form_class = AnswerForm
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        return context

    def get_queryset(self):
        pk = self.kwargs['pk']
        question = Question.objects.get(pk=pk)
        return Answer.objects.filter(question=question).order_by('-total_points', '-updated')

    def get_success_url(self):
        return reverse(viewname="qa:qa_detail", kwargs={'pk': self.kwargs['pk']})

    def get(self, request, *args, **kwargs):
        # From ProcessFormMixin
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

        # From BaseListView
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})

        context = self.get_context_data(object_list=self.object_list, form=self.form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)

        if self.form.is_valid():
            self.object = self.form.save(commit=False)
            self.object.user = self.request.user
            self.object.question = Question.objects.get(pk=self.kwargs['pk'])
            self.object.save()
            notify.send(sender=self.object.user, recipient=self.object.question.user, actor=self.object.user,
                        verb='回答了你的问题', target=self.object,
                        description=self.object.user.username+'刚刚回答你了你提的问题"'+self.object.question.title+'",快去看看吧！')
            # Here ou may consider creating a new instance of form_class(),
            # so that the form will come clean.
        return self.get(request, *args, **kwargs)


class UpdateAnswerView(AuthorRequiredMixin, UpdateView):
    """
    Updates the question answer
    """
    template_name = 'qa/update_answer.html'
    model = Answer
    pk_url_kwarg = 'answer_id'
    fields = ['answer_text']

    def get_object(self, queryset=None):
        pk = self.kwargs['answer_id']
        return Answer.objects.get(pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['question'] = self.object.question
        return context

    def get_success_url(self):
        notify.send(sender=self.object.user, recipient=self.object.question.user, actor=self.object.user,
                    verb='更新了回答', target=self.object,
                    description=self.object.user.username + '在你的问题"'+self.object.question.title+'"下刚刚更新了回答，快去看看吧！')
        return reverse(viewname="qa:qa_detail", kwargs={'pk': self.object.question.pk})


class UpdateQuestionView(AuthorRequiredMixin, UpdateView):
    """
    Updates the question
    """
    template_name = 'qa/update_question.html'
    model = Question
    pk_url_kwarg = 'question_id'
    fields = ['title', 'description']

    def get_object(self, queryset=None):
        pk = self.kwargs['question_id']
        return Question.objects.get(pk=pk)

    def get_success_url(self):
        return reverse(viewname="qa:qa_detail", kwargs={'pk': self.object.pk})