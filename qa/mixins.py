from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic import View


class AuthorRequiredMixin(View):
    """
    check whether object's user is request.user before dispatch
    """
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise PermissionDenied

        return super(
            AuthorRequiredMixin, self).dispatch(request, *args, **kwargs)