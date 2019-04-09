from django.contrib import admin

# Register your models here.
from qa.models import Answer, Question, AnswerVote, QuestionVote

admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(AnswerVote)
admin.site.register(QuestionVote)