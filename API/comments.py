from fluent_comments.forms import CompactLabelsCommentForm
from django.conf import settings
from django import forms
from django.utils.text import get_text_list
from django.utils.translation import pgettext_lazy, ungettext, ugettext, ugettext_lazy as _
import django
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from fluent_comments.utils import get_comment_template_name, get_comment_context_data

from fluent_comments.compat import get_form as get_comments_form, get_django_model, signals, CommentPostBadRequest
from fluent_comments import appsettings
import json
import sys



class CommentForm(CompactLabelsCommentForm):

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].label = "留言"  # Changed the label

    def clean_comment(self):
        """
        If COMMENTS_ALLOW_PROFANITIES is False, check that the comment doesn't
        contain anything in PROFANITIES_LIST.
        """
        comment = self.cleaned_data["comment"]
        if (not getattr(settings, 'COMMENTS_ALLOW_PROFANITIES', False) and
                getattr(settings, 'PROFANITIES_LIST', False)):
            bad_words = [w for w in settings.PROFANITIES_LIST if w in comment.lower()]
            if bad_words:
                raise forms.ValidationError(ungettext(
                    "注意使用文明用语! 词语%s不允许使用。",
                    "注意使用文明用语! 词语%s不允许使用。",
                    len(bad_words)) % get_text_list(
                    ['"%s%s%s"' % (i[0], '-' * (len(i) - 2), i[-1])
                     for i in bad_words], ugettext('and')))
        return comment