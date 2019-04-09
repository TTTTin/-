import os

from django.conf import settings

from pinax.badges.base import Badge, BadgeAwarded, BadgeDetail
from pinax.badges.registry import badges
from scratch_api.models import User


class PointsBadge(Badge):
    slug = "points"
    levels = [
        "Bronze",
        "Silver",
        "Gold",
    ]
    events = [
        "points_awarded",
    ]
    multiple = False

    def award(self, **state):
        user = state["user"]
        print(user.username)
        points = user.username
        if points:
            return BadgeAwarded(level=3)
        if points > 10000:
            return BadgeAwarded(level=3)
        elif points > 7500:
            return BadgeAwarded(level=2)
        elif points > 0:
            return BadgeAwarded(level=1)


class ProductionNumberBadage(Badge):
    slug = 'ProductionNumber'
    levels = [BadgeDetail('首届编程周纪念章', '')]
    events = ['production_number_awarded']
    multiple = False
    image_path = "badges/badge.gif"

    def award(self, **state):
        # user = User.objects.get(username=state["user"])
        # if user.production_set.all().count() > 1:
        return BadgeAwarded(level=1)


class WarmHeartedBadage(Badge):
    slug = 'WarmHearted'
    levels = [BadgeDetail('热心参与奖章', '')]
    events = ['warm_hearted_awarded']
    multiple = False
    image_path = "badges/warm.png"

    def award(self, **state):
        # user = User.objects.get(username=state["user"])
        # if user.production_set.all().count() > 1:
        return BadgeAwarded(level=1) 


badges.register(ProductionNumberBadage)
badges.register(PointsBadge)
badges.register(WarmHeartedBadage)

