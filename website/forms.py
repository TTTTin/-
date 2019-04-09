import datetime
import re
from django.forms import ModelForm
from django import forms

from scratch_api.models import User, Class


class UserSettingForm(ModelForm):

    class Meta:
        model = User
        fields = ['name', 'sex', 'birthday', 'local_province', 'local_city', 'local_district', 'format_school',
                  'phone_number', 'self_introduction', 'note']

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        REGEX_MOBILE = "^1\d{10}$"
        p = re.compile(REGEX_MOBILE)
        if p.match(phone_number):
            return phone_number
        else:
            raise forms.ValidationError(u"手机号码不正确", code="phone_number_invalid")

    def clean_local_province(self):
        local_province = self.cleaned_data['local_province']
        if local_province == "=请选择省份=":
            return ""
        else:
            return local_province

    def clean_local_city(self):
        local_city = self.cleaned_data['local_city']
        if local_city == "=请选择城市=":
            return ""
        else:
            return local_city

    def clean_local_district(self):
        local_district = self.cleaned_data['local_district']
        if local_district == "=请选择县区=":
            return ""
        else:
            return local_district

    def clean_format_school(self):
        format_school = self.cleaned_data['format_school']
        if format_school == "=请选择学校=":
            return ""
        else:
            return format_school

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        current = datetime.date.today()
        if birthday > current:
            raise forms.ValidationError(u"日期大于当前时间", code='birthday_invalid')
        return self.cleaned_data['birthday']


class AddClassForm(forms.Form):
    classcode = forms.Field(label='班级编号')

    # class Meta:
    #     model = Class
    #     fields =['code']