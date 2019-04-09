from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View

from scratch_api.models import User, FormatClass


class AuthorRequiredMixin(View):
    """
    check whether object's user is request.user before dispatch
    """
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.username != self.request.user.username:
            return HttpResponseRedirect("/")

        return super(
            AuthorRequiredMixin, self).dispatch(request, *args, **kwargs)


class IsLoginMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return super(IsLoginMixin, self).dispatch(request, *args, **kwargs)
        else:
            # 带上next_url， 登录以后直接返回上一次请求的页面
            next_url = request.path
            return HttpResponseRedirect("/?next=" + next_url)


class MyFormatClassMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            """
                判断是否登录
            """
            try:
                format_class_id = int(kwargs["pk"])
                #未选择班级默认format_class_id 默认为0
                if format_class_id > 0:
                    format_class = FormatClass.objects.get(pk=format_class_id)
                    user = User.objects.get(username=request.user.username, format_class=format_class_id)
                elif format_class_id < 0:
                    return redirect(reverse('index', args=[]))
                return super(MyFormatClassMixin, self).dispatch(request, *args, **kwargs)

            except Exception as e:
                return redirect(reverse('index', args=[]))
        else:
            return redirect(reverse('index', args=[]))
