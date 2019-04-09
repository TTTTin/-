from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models

# Create your models here.
from scratch_api.models import BaseUser


class Question(models.Model):
    """Model class to contain every question in the forum"""
    title = models.CharField(max_length=200, blank=False, verbose_name="标题")
    description = RichTextUploadingField(verbose_name="问题描述", config_name='qa_ckeditor')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    update_date = models.DateTimeField('date updated', auto_now=True)
    user = models.ForeignKey(BaseUser)
    closed = models.BooleanField(default=False)
    positive_votes = models.IntegerField(default=0)
    negative_votes = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.total_points = self.positive_votes - self.negative_votes
        super(Question, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Answer(models.Model):
    """Model class to contain every answer in the forum and to link it
    to the proper question."""
    question = models.ForeignKey(Question)
    answer_text = RichTextUploadingField(verbose_name="回答", config_name='qa_ckeditor')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)
    user = models.ForeignKey(BaseUser)
    answer = models.BooleanField(default=False)
    positive_votes = models.IntegerField(default=0)
    negative_votes = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.total_points = self.positive_votes - self.negative_votes
        super(Answer, self).save(*args, **kwargs)

    def __str__(self):  # pragma: no cover
        return self.answer_text

    class Meta:
        ordering = ['-answer', '-pub_date']
        unique_together = [('user', 'question')]

class VoteParent(models.Model):
    """Abstract model to define the basic elements to every single vote."""
    user = models.ForeignKey(BaseUser)
    value = models.BooleanField(default=True)

    class Meta:
        abstract = True


class AnswerVote(VoteParent):
    """Model class to contain the votes for the answers."""
    answer = models.ForeignKey(Answer)

    class Meta:
        unique_together = (('user', 'answer'),)


class QuestionVote(VoteParent):
    """Model class to contain the votes for the questions."""
    question = models.ForeignKey(Question)

    class Meta:
        unique_together = (('user', 'question'),)