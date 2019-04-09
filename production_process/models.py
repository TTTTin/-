from django.db import models
from scratch_api.models import Production
# Create your models here.
from .fields import ListField
class ListTest(models.Model):
    labels = ListField()

    def __str__(self):
        return "%s " % self.labels

class Production_prosess(models.Model):
    """
    作品的动态
    """
    production_id = models.OneToOneField(Production, to_field='id')
    listforaddblock = ListField(blank=True,null=True,default=None)
    listfordelblock = ListField(blank=True,null=True,default=None)
    listforBackdrop = ListField(blank=True,null=True,default=None)
    listforChange = ListField(blank=True,null=True,default=None)
    listforChangeOp = ListField(blank=True,null=True,default=None)
    listforCostume = ListField(blank=True,null=True,default=None)
    listfordelbac = ListField(blank=True,null=True,default=None)
    listfordelcos = ListField(blank=True,null=True,default=None)
    listfordelspr = ListField(blank=True,null=True,default=None)
    listforDoubleclickBlock = ListField(blank=True,null=True,default=None)
    listforSound = ListField(blank=True,null=True,default=None)
    listforSpr = ListField(blank=True,null=True,default=None)
    listfordelsnd = ListField(blank=True,null=True,default=None)

class Production_listforaddblock(models.Model):
    """
    作品的增加列表
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    time = models.DateTimeField()
    type = models.CharField(default='',max_length =100)
    op = models.CharField(default='',max_length =100)
    loc = models.CharField(default='',max_length =100)


class Production_listfordelblock(models.Model):
    """
    作品的减少列表
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    del_time = models.DateTimeField()
    del_del = models.CharField(default='',max_length =100)
    del_op = models.CharField(default='',max_length =100)

class Production_listforDoubleclickBlock(models.Model):
    """
    作品的双击尝试
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    dou_time = models.DateTimeField()
    dou_name = models.CharField(default='doubleclick',max_length =100)
    dou_odd = models.CharField(default='block',max_length =100)
    dou_op = models.CharField(default='',max_length =100)

class Production_listforCostume(models.Model):
    """
    作品的增加造型
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    addcos_time = models.DateTimeField()
    addcos_add = models.CharField(default='',max_length =100)
    addcos_odd = models.CharField(default='costume',max_length =100)
    addcos_name = models.CharField(default='',max_length =100)
    addcos_from = models.CharField(default='',max_length =100)

class Production_listfordelcos(models.Model):
    """
    作品的删除造型
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    delcos_time = models.DateTimeField()
    delcos_del = models.CharField(default='',max_length =100)
    delcos_odd = models.CharField(default='costume',max_length =100)
    delcos_name = models.CharField(default='',max_length =100)
    delcos_from = models.CharField(default='',max_length =100)

class Production_listforBackdrop(models.Model):
    """
    作品的增加背景
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    addbac_time = models.DateTimeField()
    addbac_add = models.CharField(default='',max_length =100)
    addbac_odd = models.CharField(default='backdrop',max_length =100)
    addbac_name = models.CharField(default='',max_length =100)
    addbac_from = models.CharField(default='',max_length =100)

class Production_listfordelbac(models.Model):
    """
    作品的删除造型
    """
    # id = models.AutoField(primary_key=True)
    productions =models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    delbac_time = models.DateTimeField()
    delbac_del = models.CharField(default='',max_length =100)
    delbac_odd = models.CharField(default='backdrop',max_length =100)
    delbac_name = models.CharField(default='',max_length =100)
    delbac_from = models.CharField(default='',max_length =100)

class Production_listforSpr(models.Model):
    """
    作品的增加角色
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    addspr_time = models.DateTimeField()
    addspr_add = models.CharField(default='',max_length =100)
    addspr_odd = models.CharField(default='sprite',max_length =100)
    addspr_name = models.CharField(default='',max_length =100)
    addspr_from = models.CharField(default='',max_length =100)

class Production_listfordelspr(models.Model):
    """
    作品的删除角色
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    delspr_time = models.DateTimeField()
    delspr_del = models.CharField(default='',max_length =100)
    delspr_odd = models.CharField(default='sprite',max_length =100)
    delspr_name = models.CharField(default='',max_length =100)
    delspr_from = models.CharField(default='',max_length =100)

class Production_listforSound(models.Model):
    """
    作品的增加声音
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    addsnd_time = models.DateTimeField()
    addsnd_add = models.CharField(default='',max_length =100)
    addsnd_odd = models.CharField(default='sprite',max_length =100)
    addsnd_name = models.CharField(default='',max_length =100)
    addsnd_from = models.CharField(default='',max_length =100)

class Production_listfordelsnd(models.Model):
    """
    作品的删除声音
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    delsnd_time = models.DateTimeField()
    delsnd_del = models.CharField(default='',max_length =100)
    delsnd_odd = models.CharField(default='sprite',max_length =100)
    delsnd_name = models.CharField(default='',max_length =100)
    delsnd_from = models.CharField(default='',max_length =100)

class Production_listforChange(models.Model):
    """
    作品的修改资源信息
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    change_time = models.DateTimeField()
    change_change = models.CharField(default='change',max_length =100)
    change_odd = models.CharField(default='',max_length =100)
    change_pername = models.CharField(default='',max_length =100)
    change_nowname = models.CharField(default='',max_length =100)

class Production_listforChangeOp(models.Model):
    """
    作品的修改块类型
    """
    # id = models.AutoField(primary_key=True)
    productions = models.ForeignKey('scratch_api.Production',to_field='id',default=None)
    change_time = models.DateTimeField()
    change_change = models.CharField(default='change',max_length =100)
    change_odd = models.CharField(default='',max_length =100)
    change_perop= models.CharField(default='',max_length =100)
    change_nowop = models.CharField(default='',max_length =100)