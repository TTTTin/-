from django import forms
from django.conf import settings
from qa.models import Question, Answer


class QuestionForm(forms.ModelForm):
    """
    question form
    """
    class Meta:
        model = Question
        fields = ['title', 'description']


class AnswerForm(forms.ModelForm):
    """
    answer form
    """
    class Meta:
        model = Answer
        fields = ['answer_text']