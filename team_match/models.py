from random import randrange

from django.db import models

# Create your models here.
from jsonfield import JSONField

from scratch_api.models import Production, CompetitionQuestion

CHARSET = '0123456789ABCDEFGHJKMNPQRSTVWXYZabcdefghijklmnpqrstuvwxyz'
LENGTH = 16

class ProductionForBattle(models.Model):
    KIND_CHOICES = (
        (0, "其它"),
        (1, "五子棋"),
        (2, "贪吃蛇")
    )
    production = models.ForeignKey(Production, verbose_name="作品", default=None, on_delete=models.CASCADE)
    kind_of_battle = models.IntegerField(verbose_name="作品的游戏类型", choices=KIND_CHOICES, default=0)

    def __str__(self):
        return self.KIND_CHOICES[self.kind_of_battle][1] + ":" + self.production.name

    class Meta:
        unique_together = (("production"), )

class MatchProduction(models.Model):
    """
    参赛作品表
    胜：积2分
    平：积1分
    负：积0分
    """
    com_question = models.ForeignKey(CompetitionQuestion, verbose_name="竞赛题目", default=None)
    production = models.ForeignKey(ProductionForBattle, verbose_name="参赛作品", default=None)
    group = models.IntegerField(verbose_name="分组")
    score = models.IntegerField(verbose_name="积分", default=0)

    def __str__(self):
        return self.production.production.author.username + ":" + self.production.production.name

    class Meta:
        unique_together = (("production", "com_question"), )


class MatchArrange(models.Model):
    """
    对抗赛列表
    type:  0:小组赛     1:第一轮   2:第二轮   。。。
    result: -1:left胜    1: right胜
    """
    RESULT_CHOICES = (
        (-1, "左侧胜"),
        (0, "对战中"),
        (1, "右侧胜"),
        (2, "尚未开始"),
    )
    TYPE_CHOICE = (
        (0, "小组赛"),
        (1, "第一轮淘汰赛")
    )
    left = models.ForeignKey(MatchProduction, verbose_name="左侧选手", related_name="left")
    right = models.ForeignKey(MatchProduction, verbose_name="右侧选手", related_name="right")
    type = models.IntegerField(verbose_name="类型", choices=TYPE_CHOICE, default=0)
    result = models.IntegerField(verbose_name="结果", choices=RESULT_CHOICES, default=2)

    def __str__(self):
        return self.left.production.production.author.name + " : " + self.right.production.production.author.name

    class Meta:
        unique_together = (("left", "right", "type"), )


class MatchGame(models.Model):
    """
    对局列表
    code: 加入对局的秘钥
    """
    KIND_CHOICES = (
        (-1, "左侧先手"),
        (1, "右侧先手")
    )
    RESULT_CHOICES = (
        (-1, "左侧胜"),
        (0, "对战中"),
        (1, "右侧胜"),
        (2, "尚未开始"),
    )
    arrange = models.ForeignKey("MatchArrange", verbose_name="对抗赛")
    game = models.IntegerField(verbose_name="场次", default=1)
    kind = models.IntegerField(verbose_name="先后顺序", choices=KIND_CHOICES, default=-1)
    # code = models.CharField(verbose_name="代码", max_length=LENGTH, blank=True, null=True)
    result = models.IntegerField(verbose_name="结果", choices=RESULT_CHOICES, default=2)

    class Meta:
        unique_together = (("arrange", "game", ), )

    def __str__(self):
        return self.arrange.__str__() + "(第" + str(self.game) + "场)"

    # def save(self, *args, **kwargs):
    #     unique = False
    #     while not unique and not self.code.strip():
    #         new_code = ""
    #         for i in range(LENGTH):
    #             new_code += CHARSET[randrange(0, len(CHARSET))]
    #         if not MatchGame.objects.filter(code=new_code).exists():
    #             unique = True
    #             self.code = new_code
    #     super(MatchGame, self).save(*args, **kwargs)


class GameDetail(models.Model):
    """
    对局详情列表
    """
    match_game = models.ForeignKey("MatchGame", verbose_name="对局id")
    operator = models.ForeignKey("MatchProduction", verbose_name="执行者")
    round = models.IntegerField(verbose_name="回合")
    detail = JSONField(verbose_name="具体内容")

    class Meta:
        unique_together = (("match_game", "round", ), )

    def __str__(self):
        return self.match_game.__str__() + "--第" + str(self.round) + "回合"



