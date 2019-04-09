from django import template
from django.template.defaultfilters import stringfilter
from qa.models import Answer, QuestionVote, AnswerVote

register = template.Library()


@register.assignment_tag(name='get_if_answer', takes_context=True)
def get_if_answer(context, question):
    """
    check whether a user have answered a question
    :param context: context of request
    :param question: question object
    :return: whether a user have answered a question
    """
    user = context['request'].user
    if Answer.objects.filter(user=user, question=question).exists():
        return True
    else:
        return False


@register.simple_tag(name='get_update_answer_pk', takes_context=True)
def get_update_answer_pk(context, question):
    """
    :param context: context of request
    :param question: question object
    :return: primary key of answer that user answered in `question`
    """
    user = context['request'].user
    answer = Answer.objects.get(user=user, question=question)
    return answer.pk


@register.assignment_tag(name='get_answer_count')
def get_answer_count(question):
    """
    get answer count of a question
    :param question: question object
    :return: answer count of a question
    """
    return Answer.objects.filter(question=question).count()


@register.assignment_tag(name='get_question_vote_status', takes_context=True)
def get_question_vote_status(context, question):
    """
    return status that whether a user have voted a question
    :param context: context of request
    :param question: question object
    :return: +1,-1 or 0(means that not vote)
    """
    user = context['request'].user
    if user.is_anonymous():
        return 0
    queryset = QuestionVote.objects.filter(question=question, user=user)
    if queryset.exists():
        obj = queryset.first()
        if obj.value == True:
            return 1
        else:
            return -1
    else:
        return 0


@register.assignment_tag(name='get_answer_vote_status', takes_context=True)
def get_answer_vote_status(context, answer):
    """
    similar to get_question_vote_status
    :param context:
    :param answer:
    :return:
    """
    user = context['request'].user
    if user.is_anonymous():
        return 0
    queryset = AnswerVote.objects.filter(answer=answer, user=user)
    if queryset.exists():
        obj = queryset.first()
        if obj.value == True:
            return 1
        else:
            return -1
    else:
        return 0


@register.filter(name='upto')
@stringfilter
def upto(value, delimiter=','):
    """
    this template tag used for discard format after delimiter
    for example, `"1天, 17小时"|upto` will return "一天"
    :param value: input
    :param delimiter:
    :return:
    """
    return value.split(delimiter)[0]
upto.is_safe = True



