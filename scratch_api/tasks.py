#coding=utf-8
from __future__ import unicode_literals,print_function

import requests
from notifications.signals import notify

from API.celery import app
from gen.Gen import gen,gen_block_count
import os
from API.settings import MEDIA_ROOT
from .models import Production, ProductionHint, ANTLRScore, Production_profile, EthereumQuesProScore, \
    QuestionProductionScore
from .models import User, School, Class, Teacher, CompetitionUser, Competition, Adviser,Position, FormatSchool, FormatClass
import xlrd
import re
from kombu.utils import json
#
@app.task(bind=False)
def import_student_excel(file, teacher):
    try:
        workbook = xlrd.open_workbook(file_contents=file)
        for sheet in workbook.sheets():
            nrows = sheet.nrows
            for row in range(1, nrows):
                values = sheet.row_values(row)
                values[0] = re.sub('\s', "", values[0])
                values[1] = re.sub('\s', "", values[1])
                values[2] = re.sub('\s', "", values[2])
                values[3] = re.sub('\s', "", values[3])
                values[4] = re.sub('\s', "", values[4])
                values[5] = re.sub('\s', "", values[5])
                school = School(values[0])
                school.save()
                if(len(values)==7):
                    # values[6] = re.sub('\s', "", values[6])
                    x=values[6][0:4]
                    y=values[6][4:6]
                    z=values[6][6:8]
                    list1=[x,y,z]
                    values[6]='-'.join(list1)
                class_, created = Class.objects.get_or_create(school_name=school, class_name=values[1])
                class_.save()
                class_.teacher.add(teacher)
                if User.objects.filter(username=values[2]).exists():
                    num_=len(User.objects.filter(username__contains=values[2]))
                    if (len(values) == 7):
                        user = User(username=values[2]+str(num_), name=values[2], sex=values[3], birthday=values[5],
                                    school=school, student_id=values[4],
                                    student_class=class_)
                    else:
                        user = User(username=values[2]+str(num_), name=values[2], sex=values[3],
                                    school=school, student_id=values[4],
                                    student_class=class_)
                    user.set_password("123456")
                    user.save()
                    user.classes.add(class_)
                    notify.send(sender=teacher, recipient=teacher, actor=teacher,
                                verb='批量注册时发现重名', description='在批量注册时，发现用户名"'+values[2]+'"已经存在，已更换为"'+values[2]+str(num_))
                    continue
                if(len(values)==7):
                    user = User(username=values[2], name=values[2], sex=values[3], birthday=values[5], school=school, student_id=values[4],
                            student_class=class_)
                else:
                    user = User(username=values[2], name=values[2], sex=values[3],
                                school=school, student_id=values[4],
                                student_class=class_)
                user.set_password("123456")
                user.save()
                user.classes.add(class_)
    except Exception as e:
        print(e)
        notify.send(sender=teacher, recipient=teacher, actor=teacher,
                    verb='批量上传学生名单失败', description="批量上传学生名单失败，可能因为您上传的excel中格式存在问题，请认真与模版excel核对后再上传，"
                                                   "如果仍然存在问题，请联系管理员")

@app.task(bind=False)
def import_teacher_excel(file, teacher, province, city, country, school):
    try:
        workbook = xlrd.open_workbook(file_contents=file)
        for sheet in workbook.sheets():
            nrows = sheet.nrows
            for row in range(1, nrows):
                values = sheet.row_values(row)
                values[0] = re.sub('\s', "", values[0])
                values[1] = re.sub('\s', "", values[1])
                values[2] = re.sub('\s', "", values[2])
                school = FormatSchool.objects.get(province=province, city=city, district=country, name=school)
                print(school)
                if Teacher.objects.filter(username=values[2]).exists():
                    notify.send(sender=teacher, recipient=teacher, actor=teacher,
                                verb='批量注册教师时发现该手机号已注册',
                                description='在批量注册时，发现手机号为："' + values[2] + '"的教师已注册，注册失败"')
                else:
                    teacher = Teacher(username=values[2], name=values[0], email=values[1], phone_number=values[2], format_school=school)
                    teacher.set_password("123456")
                    teacher.save()

    except Exception as e:
        notify.send(sender=teacher, recipient=teacher, actor=teacher,
                    verb='批量上传教师名单失败', description="批量上传教师名单失败，可能因为您上传的excel中格式存在问题，请认真与模版excel核对后再上传，"
                                                   "如果仍然存在问题，请联系管理员")

# @app.task(bind=False)
# def import_competition_user_excel(file, teacher):
#     try:
#         workbook = xlrd.open_workbook(file_contents=file)
#         for sheet in workbook.sheets():
#             nrows = sheet.nrows
#             for row in range(1, nrows):
#                 values = sheet.row_values(row)
#                 values[0] = re.sub('\s', "", values[0])
#                 values[1] = re.sub('\s', "", values[1])
#                 values[2] = re.sub('\s', "", values[2])
#                 values[3] = re.sub('\s', "", values[3])
#                 values[4] = re.sub('\s', "", values[4])
#                 values[5] = re.sub('\s', "", values[5])
#                 values[6] = re.sub('\s', "", values[6])
#                 values[7] = re.sub('\s', "", values[7])
#                 if Competition.objects.filter(title=values[3]).exists():
#                     competition1 = Competition.objects.get(title=values[3])
#                     school1 = School.objects.get(school_name=values[0])
#                     class1 =values[1]
#                     if User.objects.filter(name=values[2], school=school1, classes__class_name__contains=class1).exists():
#                         len1=len(User.objects.filter(name=values[2], school=school1, classes__class_name__contains=class1))
#                         print(len1)
#                         if len1>=2:
#                             notify.send(sender=teacher, recipient=teacher, actor=teacher,
#                                         verb='批量报名失败', description="批量报名失败，"+class1+"班" + values[2] + "学生出现重名情况")
#                         else:
#                             user1 = User.objects.get(name=values[2], school=school1, classes__class_name__contains=class1)
#                             if Teacher.objects.filter(name=values[5]) .exists():
#                                 len2 = len(Teacher.objects.filter(name=values[5]))
#                                 if len2 >= 2:
#                                     notify.send(sender=teacher, recipient=teacher, actor=teacher,
#                                                 verb='批量报名失败', description="批量报名失败，" + values[5] + "教师出现重名情况")
#                                 else:
#                                     teacher1 = Teacher.objects.get(name=values[5])
#                                     teacher1.phone_number=values[6]
#                                     teacher1.save()
#                                     if CompetitionUser.objects.filter(competition=competition1, user=user1,
#                                                                       tutor=teacher1).exists():
#                                         pass
#                                     else:
#                                         competition_user = CompetitionUser(competition=competition1, user=user1,
#                                                                            tutor=teacher1)
#                                         competition_user.save()
#                             else:
#                                 notify.send(sender=teacher, recipient=teacher, actor=teacher,
#                                         verb='批量报名失败', description="批量报名失败，" + values[5] + "教师不存在")
#                     else:
#                         notify.send(sender=teacher, recipient=teacher, actor=teacher,
#                                     verb='批量报名失败', description="批量报名失败，"+values[2]+"用户不存在")
#                 else:
#                     notify.send(sender=teacher, recipient=teacher, actor=teacher,
#                                 verb='批量报名失败', description="批量报名失败，"+values[3]+"竞赛不存在")
#     except Exception as e:
#         print(e)
#         notify.send(sender=teacher, recipient=teacher, actor=teacher,
#                     verb='批量报名失败', description="批量报名失败，可能因为您上传的excel中格式存在问题，请认真与模版excel核对后再上传，"
#                                                    "如果仍然存在问题，请联系管理员")
#


@app.task(bind=False)
def import_competition_user_excel(file, teacher):
    try:
        workbook = xlrd.open_workbook(file_contents=file)
        for sheet in workbook.sheets():
            nrows = sheet.nrows
            for row in range(1, nrows):
                values = sheet.row_values(row)
                values[0] = re.sub('\s', "", values[0])
                values[1] = re.sub('\s', "", values[1])
                values[2] = re.sub('\s', "", values[2])
                values[3] = re.sub('\s', "", values[3])
                values[4] = re.sub('\s', "", values[4])
                if Competition.objects.filter(title=values[2]).exists():
                    competition1 = Competition.objects.get(title=values[2])
                    if User.objects.filter(name=values[1], username=values[0]).exists():
                        user1 = User.objects.get(name=values[1], username=values[0])
                        if Teacher.objects.filter(name=values[3], username=values[4]) .exists():
                            teacher1 = Teacher.objects.get(name=values[3], username=values[4])
                            if CompetitionUser.objects.filter(competition=competition1, user=user1, tutor=teacher1).exists():
                                pass
                            else:
                                competition_user = CompetitionUser(competition=competition1, user=user1, tutor=teacher1)
                                competition_user.save()
                        else:
                            notify.send(sender=teacher, recipient=teacher, actor=teacher, verb='批量报名失败',
                                        description="批量报名失败，" + values[3] + "教师不存在")
                    else:
                        notify.send(sender=teacher, recipient=teacher, actor=teacher,
                                    verb='批量报名失败', description="批量报名失败，"+values[1]+"用户不存在")
                else:
                    notify.send(sender=teacher, recipient=teacher, actor=teacher,
                                verb='批量报名失败', description="批量报名失败，"+values[2]+"竞赛不存在")
    except Exception as e:
        print(e)
        notify.send(sender=teacher, recipient=teacher, actor=teacher,
                    verb='批量报名失败', description="批量报名失败，可能因为您上传的excel中格式存在问题，请认真与模版excel核对后再上传，"
                                                   "如果仍然存在问题，请联系管理员")


@app.task(bind=False)
def import_school_excel(file, teacher, province, city, country):
    try:
        workbook = xlrd.open_workbook(file_contents=file)
        for sheet in workbook.sheets():
            nrows = sheet.nrows
            for row in range(1, nrows):
                values = sheet.row_values(row)
                values[0] = re.sub('\s', "", values[0])
                values[1] = re.sub('\s', "", values[1])
                if Teacher.objects.filter(username=values[1]).exists():
                    if FormatSchool.objects.filter(name=values[0], province=province, city=city,
                                                   district=country).exists():
                        notify.send(sender=teacher, recipient=teacher, actor=teacher,
                                    verb='批量注册学校时发现重名',
                                    description='在批量注册时，发现"' + province + city + country + '"的学校"' + values[
                                        0] + '"已经存在，注册失败"')
                    else:
                        newschool = FormatSchool(name=values[0], province=province, city=city, district=country,
                                                 chief=Teacher.objects.get(username=values[1]))
                        newschool.save()
                else:
                    notify.send(sender=teacher, recipient=teacher, actor=teacher,
                                verb='批量注册学校时发现负责人不存在',
                                description='在批量注册时，发现用户名为："' + values[1] + '"的教师不存在，注册学校失败"')

    except Exception as e:
        print(e)
        notify.send(sender=teacher, recipient=teacher, actor=teacher,
                    verb='批量报名失败', description="批量报名失败，可能因为您上传的excel中格式存在问题，请认真与模版excel核对后再上传，"
                                                   "如果仍然存在问题，请联系管理员")


@app.task(bind=False)
def import_user_excel(file, teacher, province, city, country, school, class_):
    try:
        workbook = xlrd.open_workbook(file_contents=file)
        for sheet in workbook.sheets():
            nrows = sheet.nrows
            for row in range(1, nrows):
                values = sheet.row_values(row)
                values[0] = re.sub('\s', "", values[0])
                values[1] = re.sub('\s', "", values[1])
                values[2] = re.sub('\s', "", values[2])
                values[3] = re.sub('\s', "", values[3])
                values[4] = re.sub('\s', "", values[4])
                values[5] = re.sub('\s', "", values[5])
                values[6] = re.sub('\s', "", values[6])
                school = FormatSchool.objects.get(province=province, city=city, district=country, name=school)
                print(school)
                class1 = FormatClass.objects.get(format_school=school, pk=class_)
                print(class_)
                print(class1)
                if User.objects.filter(username=values[2]).exists():
                    notify.send(sender=teacher, recipient=teacher, actor=teacher,
                                verb='批量注册用户时发现该学籍号已注册',
                                description='在批量注册时，发现学籍号为："' + values[2] + '"的用户已注册，注册失败"')
                else:
                    user = User(username=values[2], name=values[0], sex=values[1], student_id=values[3], birthday=values[4], phone_number=values[5],
                                format_school=school, note=values[6])
                    user.set_password("123456")
                    user.save()
                    print("hello world")
                    print(class1)
                    user.format_class.add(class1)
                    user.save()

    except Exception as e:
        print(e)
        notify.send(sender=teacher, recipient=teacher, actor=teacher,
                    verb='批量上传学生名单失败', description="批量上传学生名单失败，可能因为您上传的excel中格式存在问题，请认真与模版excel核对后再上传，"
                                                   "如果仍然存在问题，请联系管理员")


@app.task(bind=False)
def import_class_excel(file, teacher, province, city, country, school, grade, class_num):
    try:
        workbook = xlrd.open_workbook(file_contents=file)
        for sheet in workbook.sheets():
            nrows = sheet.nrows
            for row in range(1, nrows):
                values = sheet.row_values(row)
                values[0] = re.sub('\s', "", values[0])
                values[1] = re.sub('\s', "", values[1])
                values[2] = re.sub('\s', "", values[2])
                values[3] = re.sub('\s', "", values[3])
                values[4] = re.sub('\s', "", values[4])
                values[5] = re.sub('\s', "", values[5])
                values[6] = re.sub('\s', "", values[6])

                # school = FormatSchool.objects.get(province=province, city=city, district=country, name=school)
                # print(school)
                # class1 = FormatClass.objects.get(format_school=school, pk=class_)
                # print(class_)
                # print(class1)
                # if User.objects.filter(username=values[2]).exists():
                #     notify.send(sender=teacher, recipient=teacher, actor=teacher,
                #                 verb='批量注册用户时发现该学籍号已注册',
                #                 description='在批量注册时，发现学籍号为："' + values[2] + '"的用户已注册，注册失败"')
                # else:
                #     user = User(username=values[2], name=values[0], sex=values[1], student_id=values[3], birthday=values[4], phone_number=values[5],
                #                 format_school=school, note=values[6])
                #     user.set_password("123456")
                #     user.save()
                #     print("hello world")
                #     print(class1)
                #     user.format_class.add(class1)
                #     user.save()

    except Exception as e:
        print(e)
        notify.send(sender=teacher, recipient=teacher, actor=teacher,
                    verb='批量上传学生名单失败', description="批量上传学生名单失败，可能因为您上传的excel中格式存在问题，请认真与模版excel核对后再上传，"
                                                   "如果仍然存在问题，请联系管理员")


@app.task(bind=False)
def add(x, y):
    return x+y

@app.task(bind=False)
def run(production_id, path):
    absolute_path = os.path.join(MEDIA_ROOT, path)
    score, hints ,profile = gen(absolute_path)
    production = Production.objects.get(id=production_id)

    # Create or Update antlr score
    antlr_score = ANTLRScore.objects.filter(production_id=production)
    if antlr_score:
        antlr_score = antlr_score.first()
    else:
        antlr_score = ANTLRScore(production_id=production)
    antlr_score.ap_score = int(score['Abstraction'])
    antlr_score.parallelism_score = int(score['Parallelism'])
    antlr_score.synchronization_score = int(score['Synchronization'])
    antlr_score.user_interactivity_score = int(score['UserInteractivity'])
    antlr_score.flow_control_score = int(score['FlowControl'])
    antlr_score.logical_thinking_score = int(score['LogicalThinking'])
    antlr_score.data_representation_score = int(score['DataRepresentation'])
    antlr_score.code_organization_score = int(score['CodeOrganization'])
    antlr_score.content_score = int(score['Content'])
    antlr_score.save()

    antlr_profile = Production_profile.objects.filter(production_id=production)
    if antlr_profile:
        antlr_profile = antlr_profile.first()
    else:
        antlr_profile = Production_profile(production_id=production)
    antlr_profile.motion_num = int(profile['motions'])
    antlr_profile.looklike_num = int(profile['looklike'])
    antlr_profile.sounds_num = int(profile['sounds'])
    antlr_profile.draw_num = int(profile['draw'])
    antlr_profile.event_num = int(profile['event'])
    antlr_profile.control_num = int(profile['control'])
    antlr_profile.sensor_num = int(profile['sensor'])
    antlr_profile.operate_num = int(profile['operate'])
    antlr_profile.more_num = int(profile['more'])
    antlr_profile.data_num = int(profile['data'])
    antlr_profile.sprite_num = int(profile['sprites'])
    antlr_profile.backdrop_num = int(profile['backdrop'])
    antlr_profile.snd_num = int(profile['snduse'])
    antlr_profile.save()

    # Delete Hint of this production first
    objects = ProductionHint.objects.filter(production_id=production)
    objects.delete()
    # Then save the new hint
    for hint in hints:
        production_hint = ProductionHint(production_id=production, hint=hint)
        production_hint.save()


@app.task(bind=False)
def count_block(production_id, path):
    absolute_path = os.path.join(MEDIA_ROOT, path)
    blockCount = gen_block_count(absolute_path)
    # production = Production.objects.get(id=production_id)

    # Create or Update antlr_block_count

    antlr_block_count = Production.objects.filter(id=production_id)
    if antlr_block_count:
        antlr_block_count = antlr_block_count.first()
    else:
        antlr_block_count = Production(id=production_id)
    antlr_block_count.script_count = int(blockCount['scriptCount'])
    antlr_block_count.sprite_count = int(blockCount['spriteCount'])
    antlr_block_count.save()


@app.task(bind=False)
def upload_QuesProScore(id):
    quesProScore = QuestionProductionScore.objects.get(pk=id)
    address = "0x72102c0ac12cecefc0ad798f778c65541600f1d6"
    password = "123"
    # url = 'http://www.genyuanlian.org/students/uploadWorks'
    url = 'http://10.103.247.54:8080/students/uploadWorks'
    headers = {
        'content-type': 'application/json',
    }
    body = {
        "address": address,
        "password": password,
        "detail": {
            "question_id": quesProScore.question.id,
            "production_id": quesProScore.production.id,
            "rater_username": quesProScore.rater.username,
            "score": quesProScore.score,
            "small_score": quesProScore.small_score,
            "comment": quesProScore.comment,
            "score_time": quesProScore.score_time,
            "is_adviser": quesProScore.is_adviser,
        }
    }
    response = requests.post(url, data=json.dumps(body), headers=headers)
    print(response.status_code)
    response = json.loads(response.text)
    print(response)
    if response['result']:
        ethereumQuesProScore = EthereumQuesProScore()
        ethereumQuesProScore.question = quesProScore.question
        ethereumQuesProScore.production = quesProScore.production
        ethereumQuesProScore.rater = quesProScore.rater
        ethereumQuesProScore.score_time = quesProScore.score_time
        ethereumQuesProScore.hash = response['hash']
        ethereumQuesProScore.save()
        get_QuesProScore.delay(id)
    else:
        print("error", response)


@app.task(bind=False)
def get_QuesProScore(id):
    # url = "http://www.genyuanlian.org/students/getWorkDetail"
    url = "http://10.103.247.54:8080/students/getWorkDetail"
    headers = {
        'content-type': 'application/json',
    }
    quesProScore = QuestionProductionScore.objects.get(pk=id)
    all_ethereumQuesProScore = EthereumQuesProScore.objects.filter(
        question=quesProScore.question,
        production=quesProScore.production,
        rater=quesProScore.rater,
    )
    for ethereumQuesProScore in all_ethereumQuesProScore:
        body = {
            "hash": ethereumQuesProScore.hash
        }
        response = requests.post(url, data=json.dumps(body), headers=headers)
        print(response.status_code)
        response = json.loads(response.text)
        print(response)


