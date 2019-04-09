#coding=utf-8
from __future__ import print_function, unicode_literals

from scratch_api.models import User, School, Class, Teacher
import xlrd
from datetime import datetime
from xlrd import xldate_as_tuple

def import_student_excel(file, teacher):
    workbook = xlrd.open_workbook(file_contents=file)
    for sheet in workbook.sheets():
        nrows = sheet.nrows
        for row in range(1, nrows):
            values = sheet.row_values(row)
            school = School(values[0])
            school.save()
            strs='-'
            # print(len(values[6] and strs))
            # if(len(values[6] and strs)!=0):
            #     vals=values[6].split('')
            # print(len(values))
            if(len(values)==7):
                # print(type(values[6]))
                x=values[6][0:4]
                y=values[6][4:6]
                z=values[6][6:8]
                list1=[x,y,z]
                values[6]='-'.join(list1)
                # print(values[6])
            # datebir=datetime(*xldate_as_tuple(values[1], 0))
            # values[1]=datebir.strftime("%Y-%d-%m")
            class_, created = Class.objects.get_or_create(school_name=school, class_name=values[1])
            class_.save()
            teacher = Teacher.objects.get(username="test")
            class_.teacher.add(teacher)
            if(len(values)==7):
                user = User(username=values[2], name=values[2], sex=values[3], birthday=values[5], school=school, student_id=values[4],
                        student_class=class_)
            else:
                user = User(username=values[2], name=values[2], sex=values[3],
                            school=school, student_id=values[4],
                            student_class=class_)
            # user = User(username= values[2], name=values[2], birthday=values[1], sex=values[2], grade=values[3], school=school,
            #             student_id = values[8], phone_number = values[9],
            #             local_province = values[10], local_city = values[11], local_district = values[12],
            #             student_class = class_)
            user.set_password("123456")
            user.save()
            # for val in values:
            #     print(val)
    pass



