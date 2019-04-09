import json

from django.http import HttpResponse

from qa.models import Question, AnswerVote, QuestionVote, Answer
from scratch_api.models import BaseUser


def ajax_vote_question(request, question, value):
    """
    ajax vote a question
    :param request:
    :param question: pk of a question
    :param value: '1' means +1, '0' means -1
    :return: a json contains result
    """
    baseuser = request.user
    response_data = {}
    user = BaseUser.objects.get(username=baseuser)
    question = Question.objects.get(pk=question)
    if not QuestionVote.objects.filter(user=user, question=question).exists():
        if value == '1':
            question.positive_votes += 1
            QuestionVote(user=user, question=question, value=True).save()
        else:
            question.negative_votes += 1
            QuestionVote(user=user, question=question, value=False).save()
        question.save(update_fields=['positive_votes', 'negative_votes', 'total_points'])
        response_data['result'] = 'Success!'
    else:
        response_data['result'] = "重复投票!"
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def ajax_vote_answer(request, answer, value):
    """
    ajax vote a answer
    :param request:
    :param answer: pk of a answer
    :param value: '1' means +1, '0' means -1
    :return: a json contains result
    """
    baseuser = request.user
    response_data = {}
    user = BaseUser.objects.get(username=baseuser)
    answer = Answer.objects.get(pk=answer)
    if not AnswerVote.objects.filter(user=user, answer=answer).exists():
        if value == '1':
            answer.positive_votes += 1
            AnswerVote(user=user, answer=answer, value=True).save()
        else:
            answer.negative_votes += 1
            AnswerVote(user=user, answer=answer, value=False).save()
        answer.save(update_fields=['positive_votes', 'negative_votes', 'total_points'])
        response_data['result'] = 'Success!'
    else:
        response_data['result'] = "重复投票!"
    return HttpResponse(json.dumps(response_data), content_type="application/json")