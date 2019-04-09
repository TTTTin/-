from django import template
from team_match.models import MatchGame
register = template.Library()


@register.simple_tag(name='get_game', takes_context=True)
def get_game(context, arrange):
    """
    :param obj: production object
    :return: count favorites of a production
    """
    games = MatchGame.objects.all().filter(arrange=arrange)
    return {'games': games, }

@register.filter(name='get_class')
def get_class(i):
    if i % 2 == 0:
        return "active"
    else:
        return "success"
