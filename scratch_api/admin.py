# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from jsonfield import JSONField
from django.forms import Widget
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from guardian.admin import GuardedModelAdmin
from import_export.admin import ImportExportActionModelAdmin

from pinax.badges.models import BadgeAward

from production_process.tasks import Product_process
from scratch_api.import_export_resources import AntiCheatingResource, AntiCheatingSummaryResource, \
    QuestionProductionScoreResource, SchoolAdminResource
from .models import User, Teacher, Production, ANTLRScore, ProductionHint, TeacherScore, School, Class, \
    FavoriteProduction, LikeProduction, CommentEachOther, Gallery, FavoriteGallery, LikeGallery, galleryproduction, \
    Position, Competition, CompetitionUser, CompetitionQuestion, QuestionProductionScore, Adviser, AntiCheating, \
    EthereumQuesProScore, DownloadSource, dataVisualization, FormatSchool, FormatClass

from scratch_api.tasks import run
from django.contrib.auth.models import Permission
# Register your models here.

#  ----------------------START OF CUSTOM USER ADMIN-----------------------------------------------


class JsonEditorWidget(Widget):
    """
    在 django  admin 后台中使用  jsoneditor 处理 JSONField

    TODO：有待改进, 这里使用 % 格式化，使用 format 会抛出 KeyError 异常
    """

    html_template = """
    <div id='%(name)s_editor_holder' style='padding-left:170px'></div>
    <textarea hidden readonly class="vLargeTextField" cols="40" id="id_%(name)s" name="%(name)s" rows="20">%(value)s</textarea>

    <script type="text/javascript">
        var element = document.getElementById('%(name)s_editor_holder');
        var json_value = %(value)s;

        var %(name)s_editor = new JSONEditor(element, {
            onChange: function() {
                var textarea = document.getElementById('id_%(name)s');
                var json_changed = JSON.stringify(%(name)s_editor.get()['Object']);
                textarea.value = json_changed;
            }
        });

        %(name)s_editor.set({"Object": json_value})
        %(name)s_editor.expandAll()
    </script>
    """

    def __init__(self, attrs=None):
        super(JsonEditorWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if isinstance(value, str):
            value = json.loads(value)

        result = self.html_template % {'name': name, 'value': json.dumps(value),}
        return mark_safe(result)


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'name', 'sex', 'grade', 'student_id', 'school',
                  'student_class', 'school_second', 'student_class_second', 'password1', 'password2')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username', 'name', 'sex', 'grade', 'student_id', 'school',
                  'student_class', 'school_second', 'student_class_second')
        readonly_fields = ('created_at', )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ['username', 'name', 'sex', 'school', 'school_second']
    filter_horizontal = ('format_class', )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'name', 'sex', 'grade',
                       'format_school', 'format_class', 'enrollment_number', 'note',
                       'birthday', 'local_province', 'local_city', 'local_district',
                       'student_id','school', 'student_class', 'school_second', 'student_class_second',
                       'phone_number', 'self_introduction')}
         ),
    )

    list_filter = ('school', 'classes')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('name', 'student_id', 'sex', 'grade',
                                         'format_school', 'format_class', 'enrollment_number', 'note',
                                         'birthday', 'local_province', 'local_city', 'local_district',
                                         'school', 'student_class', 'school_second', 'student_class_second',
                                         'classes', 'phone_number', 'self_introduction')},
         ),
    )

    search_fields = ('username', 'name', 'school__school_name', 'classes__class_name')
    ordering = ('username',)
    filter_horizontal = ()

    class Meta:
        model = Production


#  ----------------------END OF CUSTOM USER ADMIN-----------------------------------------------


#  ----------------------START OF CUSTOM PRODUCTION ADMIN-----------------------------------------------

def re_run(modeladmin, request, queryset):
    re_run.short_description = _("重新测试")
    for production in queryset:
        run.delay(production.id, production.file.path)
        #print(production.id)
        Product_process.delay(production.id, production.file.path)
        #print(production.id)


class ProductionAdmin(admin.ModelAdmin):
    # 显示在管理页面的字段
    list_display = ['id', 'file', 'name', 'author', 'create_time', 'update_time',]
    search_fields = ('pk', 'name','author__username', 'author__name',)
    actions = [re_run]

    class Meta:
        model = Production

#  ----------------------END OF CUSTOM PRODUCTION ADMIN-----------------------------------------------


class MembershipInline(admin.TabularInline):
    model = Class.teacher.through
    extra = 1


#  ----------------------START OF CUSTOM TEACHER ADMIN-----------------------------------------------

class TeacherCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Teacher
        fields = ('username', 'email', 'name', 'phone_number', 'school', 'format_school', 'belong_adviser')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(TeacherCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class TeacherChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Teacher
        fields = ('username', 'email', 'name', 'phone_number', 'school', 'format_school', 'belong_adviser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


def reset_password(modeladmin, request, queryset):
    reset_password.short_description = _("重置密码")
    for user in queryset:
        print(user.password)
        user.set_password("123456")
        user.save()


class TeacherAdmin(BaseUserAdmin, admin.ModelAdmin):
    # The forms to add and change user instances
    form = TeacherChangeForm
    add_form = TeacherCreationForm


    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'name', 'email', 'phone_number', 'school', 'format_school', 'belong_adviser', 'position')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('name', 'email', 'phone_number', 'school', 'format_school', 'belong_adviser', 'position')}),
    )

    actions = [reset_password, ]

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'name', 'phone_number', 'school', 'format_school', 'belong_adviser', 'password1', 'password2')}
        ),
    )
    search_fields = ('username', 'name')
    ordering = ('username',)
    filter_horizontal = ()
    inlines = [MembershipInline,]


#  ----------------------END OF CUSTOM TEACHER ADMIN-----------------------------------------------


class ProductionHintAdmin(admin.ModelAdmin):
    # 显示在管理页面的字段
    list_display = ['production_id', 'hint']

    class Meta:
        model = ProductionHint


class ANTLRScoreAdmin(ImportExportActionModelAdmin):
    # 显示在管理页面的字段

    list_display = ['production_id', 'get_production_name', 'ap_score', 'parallelism_score',
                    'synchronization_score', 'flow_control_score', 'user_interactivity_score',
                    'logical_thinking_score', 'data_representation_score', 'content_score',
                    'code_organization_score', 'total']
    search_fields = ('production_id__name', )

    def get_production_name(self, obj):
        return obj.production_id.name
    get_production_name.short_description = "作品名称"
    get_production_name.admin_order_field = 'production_id__name'


    class Meta:
        model = ANTLRScore

class ClassAdmin(admin.ModelAdmin):
    list_display = ['pk','school_name','class_name', 'code']
    filter_horizontal = ('teacher', )
    search_fields = ('code', 'school_name__school_name', 'class_name')
    list_filter = ('school_name',)
    class Meta:
        model = Class


def set_checked(modeladmin, request, queryset):

    for galleryproduction in queryset:
        if galleryproduction.admin_checked != True:
            galleryproduction.admin_checked = True
            galleryproduction.save()

def set_unchecked(modeladmin, request, queryset):

    for galleryproduction in queryset:
        if galleryproduction.admin_checked != False:
            galleryproduction.admin_checked = False
            galleryproduction.save()



set_checked.short_description = "标记为已检查"
set_unchecked.short_description = "标记为未检查"




class GaleryProductionAdmin(admin.ModelAdmin):
    # 显示在管理页面的字段
    # production_img = Production.image(null=True)
    # c['production_img'] = production_img
    list_display = ['gallery', 'production','admin_checked']
    # 定制过滤器
    list_filter = ('gallery','admin_checked')
    # 可查询字段
    search_fields = ('gallery',)
    # Many to many 字段
    actions = [set_checked,set_unchecked]


    #设置哪些字段可以点击进入编辑界面
    list_display_links = ('gallery','production')

    class Meta:
        model = galleryproduction


class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'permissions']
    class Meta:
        model = Position



class BadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'level']
    class Meta:
        model = BadgeAward


class AdviserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = Adviser
        fields = ('username', 'email', 'name', 'phone_number', 'local_province', 'local_city', 'local_district', 'is_boss')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(AdviserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AdviserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Adviser
        fields = ('username', 'email', 'name', 'phone_number', 'local_province', 'local_city',
                  'local_district', 'is_boss')

    def clean_password(self):
        return self.initial["password"]


class AdviserAdmin(BaseUserAdmin, admin.ModelAdmin):
    form = AdviserChangeForm
    add_form = AdviserCreationForm

    list_display = ('username', 'name', 'email', 'phone_number', 'local_province', 'local_city',
                    'local_district', 'is_boss')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('name', 'email', 'phone_number', 'local_province', 'local_city',
                                         'local_district', 'position', 'is_boss')}),
    )
    add_fieldsets = (
        (None, {
           'classes': ('wide', ),
            'fields': ('username', 'email', 'name', 'phone_number', 'local_province', 'local_city',
                       'local_district', 'position', 'is_boss', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'name')
    ordering = ('username', )
    filter_horizontal = ()
    inlines = [MembershipInline, ]


class AntiCheatingAdmin(ImportExportActionModelAdmin):
    actions = ['export_admin_action', 'export_summary_admin_action']
    resource_class = AntiCheatingResource

    def export_summary_admin_action(self, request, queryset):
        """
        Exports the selected rows using file_format.
        """
        formats = self.get_export_formats()
        file_format = formats[int(2)]()
        export_data = file_format(AntiCheatingSummaryResource.export(queryset))
        content_type = file_format.get_content_type()
        response = HttpResponse(export_data, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename=%s' % (
            self.get_export_filename(file_format),
        )
        return response

    class Meta:
        model = AntiCheating


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'creator', 'start_time', 'stop_time',)
    search_fields = ('title', 'creator__name', )
    filter_horizontal = ['rater', 'advisers', ]

    class Meta:
        model = Competition


class CommonAdminMixin(admin.ModelAdmin):
    """Common Admin Mixin"""
    list_max_show_all = 20
    list_per_page = 20

    formfield_overrides = {
        JSONField: {'widget': JsonEditorWidget}
    }

    class Media:
        from django.conf import settings
        static_url = getattr(settings, 'STATIC_URL')

        css = {
            'all': (static_url + 'jsoneditor.min.css', )
        }
        js = (static_url + 'jsoneditor-minimalist.min.js', )


class QuestionProductionScoreAdmin(CommonAdminMixin):
    list_display = ['question', 'production', 'rater', 'score', 'is_adviser', ]
    search_fields = ('question__competition__title', 'question__question', 'production__author__name', 'production__name', 'rater__name')

    class Meta:
        model = QuestionProductionScore


class CompetitionQuestionAdmin(CommonAdminMixin):
    filter_horizontal = ('production', )
    list_display = ['question', 'competition', 'create_time']
    search_fields = ['question', 'competition__title', ]

    class Meta:
        model = CompetitionQuestion


class SchoolAdmin(ImportExportActionModelAdmin):
    resource_class = SchoolAdminResource
    list_display = ['school_name']
    search_fields = ['school_name']

    class Meta:
        model = School


class CompetitionUserAdmin(admin.ModelAdmin):
    list_display = ['competition', 'user', 'tutor', ]
    search_fields = ['competition__title', 'user__username', 'user__name', 'tutor__name']

    class Meta:
        model = CompetitionUser


class EthereumQuesProScoreAdmin(admin.ModelAdmin):
    list_display = ['question', 'production', 'rater', 'score_time', 'hash', ]
    search_fields = ['question__id', 'question__name', 'production__id', 'rater__username', ]

    class Meta:
        model = EthereumQuesProScore


class FormatSchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'province', 'city', 'district', 'chief', 'pk', 'add_time', 'is_active', ]
    search_fields = ['name', 'province', 'city', 'district', 'chief__name', ]

    class Meta:
        model = FormatSchool


class FormatClassAdmin(admin.ModelAdmin):
    list_display = ['show_grade_class', 'format_school', 'chief', 'is_interest', 'pk', 'add_time', 'is_active', ]
    search_fields = ['format_school__name', 'chief__name', ]

    def show_grade_class(self, obj):
        return str(obj.grade) + "年级" + str(obj.class_num) + "班"

    show_grade_class.short_description = "班级"
    show_grade_class.allow_tag = True

    class Meta:
        model = FormatClass


admin.site.register(User, UserAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Production, ProductionAdmin)
admin.site.register(ANTLRScore, ANTLRScoreAdmin)
admin.site.register(ProductionHint, ProductionHintAdmin)
admin.site.register(TeacherScore)
admin.site.register(School, SchoolAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(FavoriteProduction)
admin.site.register(LikeProduction)
admin.site.register(CommentEachOther)
admin.site.register(Gallery)
admin.site.register(FavoriteGallery)
admin.site.register(LikeGallery)
admin.site.register(galleryproduction,GaleryProductionAdmin)
admin.site.register(BadgeAward, BadgeAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(CompetitionQuestion, CompetitionQuestionAdmin)
admin.site.register(CompetitionUser, CompetitionUserAdmin)
admin.site.register(QuestionProductionScore, QuestionProductionScoreAdmin)
admin.site.register(Adviser, AdviserAdmin)
admin.site.register(AntiCheating, AntiCheatingAdmin)
admin.site.register(EthereumQuesProScore, EthereumQuesProScoreAdmin)
admin.site.register(DownloadSource)
admin.site.register(dataVisualization)
admin.site.register(FormatSchool, FormatSchoolAdmin)
admin.site.register(FormatClass, FormatClassAdmin)