#coding=utf-8
from __future__ import unicode_literals,print_function

#from bokeh.core.properties import Datetime
from notifications.signals import notify

from API.celery import app
from modulenum.getArray import getArray
import os
from API.settings import MEDIA_ROOT
from scratch_api.models import Production
from .models import Production_prosess,Production_listforaddblock,Production_listfordelsnd,Production_listforSpr,Production_listforSound,Production_listforDoubleclickBlock,Production_listfordelspr,Production_listfordelcos,Production_listfordelbac,Production_listforCostume,Production_listforChangeOp,Production_listforChange,Production_listforBackdrop,Production_listfordelblock
import xlrd
from kombu.utils import json

@app.task(bind=False)
def Product_process(production_id, path):
    absolute_path = os.path.join(MEDIA_ROOT, path)
    # print(absolute_path)
    listforaddblock, listfordelblock, listforBackdrop, listforChange,listforChangeOp,listforCostume,listfordelbac,listfordelcos,listfordelspr,listforDoubleclickBlock,listforSound,listforSpr,listfordelsnd= getArray(absolute_path)
    production = Production.objects.get(id=production_id)
    delblockpre = Production_listfordelblock.objects.filter(productions=production)
    addbacpre = Production_listforBackdrop.objects.filter(productions=production)
    changepre = Production_listforChange.objects.filter(productions=production)
    changeoppre = Production_listforChangeOp.objects.filter(productions=production)
    addcospre = Production_listforCostume.objects.filter(productions=production)
    delbacpre = Production_listfordelbac.objects.filter(productions=production)
    delcospre = Production_listfordelcos.objects.filter(productions=production)
    delsprpre = Production_listfordelspr.objects.filter(productions=production)
    doublepre = Production_listforDoubleclickBlock.objects.filter(productions=production)
    addsndpre = Production_listforSound.objects.filter(productions=production)
    addsprpre = Production_listforSpr.objects.filter(productions=production)
    delsndpre = Production_listfordelsnd.objects.filter(productions=production)
    addblockpre = Production_listforaddblock.objects.filter(productions=production)
    if delblockpre:
        delblockpre.delete()
    if addbacpre:
        addbacpre.delete()
    if changepre:
        changepre.delete()
    if changeoppre:
        changeoppre.delete()
    if addcospre:
        addcospre.delete()
    if delbacpre:
        delbacpre.delete()
    if delcospre:
        delcospre.delete()
    if delsprpre:
        delsprpre.delete()
    if doublepre:
        doublepre.delete()
    if addsndpre:
        addsndpre.delete()
    if addsprpre:
        addsprpre.delete()
    if delsndpre:
        delsndpre.delete()
    if addblockpre:
        addblockpre.delete()
    if listforaddblock:
        for i in listforaddblock:
            if i:
                Production_listforaddblock.objects.create(productions=production,time=i[0],type=i[1],loc=i[2],op=i[3])
    if listfordelblock:
        for i in listfordelblock:
            if i:
                Production_listfordelblock.objects.create(productions=production,del_time=i[0],del_del=i[1],del_op=i[2])
    if listforBackdrop:
        for i in listforBackdrop:
            if i:
                Production_listforBackdrop.objects.create(productions=production,addbac_time=i[0],addbac_add=i[1],addbac_odd=i[2],addbac_name=i[3],addbac_from=i[4])
    if listforChangeOp:
        for i in listforChangeOp:
            if i:
                Production_listforChangeOp.objects.create(productions=production,change_time=i[0],change_change=i[1],change_odd=i[2],change_perop=i[3],change_nowop=i[4])
    if listforChange:
        for i in listforChange:
            if i:
                Production_listforChange.objects.create(productions=production,change_time=i[0],change_change=i[1],change_odd=i[2],change_pername=i[3],change_nowname=i[4])
    if listforCostume:
        for i in listforCostume:
            if i:
                Production_listforCostume.objects.create(productions=production,addcos_time=i[0],addcos_add=i[1],addcos_odd=i[2],addcos_name=i[3],addcos_from=i[4])
    if listfordelbac:
        for i in listfordelbac:
            if i:
                Production_listfordelbac.objects.create(productions=production,delbac_time=i[0],delbac_del=i[1],delbac_odd=i[2],delbac_name=i[3],delbac_from=i[4])
    if listfordelcos:
        for i in listfordelcos:
            if i:
                Production_listfordelcos.objects.create(productions=production,delcos_time=i[0],delcos_del=i[1],delcos_odd=i[2],delcos_name=i[3],delcos_from=i[4])
    if listfordelspr:
        for i in listfordelspr:
            if i:
                Production_listfordelspr.objects.create(productions=production,delspr_time=i[0],delspr_del=i[1],delspr_odd=i[2],delspr_name=i[3],delspr_from=i[4])
    if listfordelsnd:
        for i in listfordelsnd:
            if i:
                Production_listfordelsnd.objects.create(productions=production,delsnd_time=i[0],delsnd_del=i[1],delsnd_odd=i[2],delsnd_name=i[3],delsnd_from=i[4])
    if listforDoubleclickBlock:
        for i in listforDoubleclickBlock:
            if i:
                Production_listforDoubleclickBlock.objects.create(productions=production,dou_time=i[0],dou_name=i[1],dou_odd=i[2],dou_op=i[3])

    if listforSound:
        for i in listforSound:
            if i:
                Production_listforSound.objects.create(productions=production,addsnd_time=i[0],addsnd_add=i[1],addsnd_odd=i[2],addsnd_name=i[3],addsnd_from=i[4])

    if listforSpr:
        for i in listforSpr:
            if i:
                Production_listforSpr.objects.create(productions=production,addspr_time=i[0],addspr_add=i[1],addspr_odd=i[2],addspr_name=i[3],addspr_from=i[4])




