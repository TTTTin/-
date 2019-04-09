# encoding=utf-8
from __future__ import unicode_literals

import re
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext, ugettext_lazy as _

from scratch_api.models import Teacher, BaseUser, User, Class, FormatSchool
from scratch_api.admin import UserCreationForm as UCF

class MyAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': "用户名"}),
        label=_("用户名"),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "密码"}, ),
    )


class SignUpForm(UserCreationForm):

    username = forms.CharField(max_length=200, label="用户名")

    password1 = forms.CharField(
        label="密码",
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="密码确认",
        widget=forms.PasswordInput,
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        # sets the placeholder key/value in the attrs for a widget
        # when the form is instantiated (so the widget already exists)
        self.fields['username'].widget.attrs['placeholder'] = '用户名'
        self.fields['name'].widget.attrs['placeholder'] = '姓名'
        self.fields['email'].widget.attrs['placeholder'] = '邮箱'
        self.fields['phone_number'].widget.attrs['placeholder'] = '手机号'
        self.fields['password1'].widget.attrs['placeholder'] = '密码长度至少8位'
        self.fields['password2'].widget.attrs['placeholder'] = '请再次确认密码'

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_username(self):
        username = self.cleaned_data['username']
        if not username:
            raise forms.ValidationError("请输入用户名")
        if BaseUser.objects.filter(username=username).exists():
            raise forms.ValidationError("该用户名已经存在")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not phone_number:
            raise forms.ValidationError("请输入手机号")
        if not phone_number.isdigit():
            raise forms.ValidationError("请输入合法的手机号")
        return phone_number

    class Meta:
        model = Teacher
        fields = ('username', 'name', 'email', 'phone_number', 'password1', 'password2')


BIRTH_YEAR_CHOICES = [i for i in range(1990, 2017)]
class UserUpdateForm(ModelForm):
    username = forms.Field(disabled=True, label="用户名")
    name = forms.Field(label="真实姓名", required=False)
    sex = forms.Field(label="性别", required=False)
    # grade=forms.Field(label="年级",required=False)
    # student_id = forms.IntegerField(label="学号", required=False)
    birthday = forms.DateField(label="生日", widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES), required=False)
    phone_number = forms.Field(label="监护人电话", required=False)


    class Meta:
        model = User
        fields = ['username', 'name', 'sex', 'birthday', 'phone_number']


class TeacherSettingForm(ModelForm):
    username = forms.Field(disabled=True, label="用户名")
    name = forms.Field(label="教师姓名", required=False)
    email = forms.EmailField(label="邮箱", required=False)
    phone_number = forms.Field(label="电话", required=False)
    format_school = forms.Field(label="所在学校",required=False)

    def clean_format_school(self):
        format_school = int(self.cleaned_data["format_school"])
        if format_school == 0:
            return None
        else:
            format_school = FormatSchool.objects.get(pk=int(format_school))
            return format_school

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        p = re.compile(REGEX_MOBILE)
        if p.match(phone_number):
            return phone_number
        else:
            raise forms.ValidationError(u"手机号码非法", code="phone_number_invalid")

    class Meta:
        model = Teacher
        fields = ['username', 'name', 'email', 'phone_number', 'format_school', ]


class TeacherChangePasswordForm(forms.Form):
    username = forms.CharField(required=True)
    old_password = forms.CharField(required=True)
    new_password1 = forms.CharField(required=True)
    new_password2 = forms.CharField(required=True)

    def clean_old_password(self):
        value = self.cleaned_data["old_password"]
        username = self.cleaned_data["username"]
        user = authenticate(username=username, password=value)
        if not user:
            raise forms.ValidationError(u"密码错误", code="old_password_invalid")
        return value

    def clean_new_password1(self):
        value = self.cleaned_data["new_password1"]
        if len(value) < 6:
            raise forms.ValidationError(u"新密码长度不能少于6位", code="new_password1_invalid")
        return value

    def clean_new_password2(self):
        new_password2 = self.cleaned_data["new_password2"]
        new_password1 = self.data["new_password1"]
        if new_password1 != new_password2:
            raise forms.ValidationError(u"两次输入的密码不一致", code="new_password2_invalid")
        return new_password2


