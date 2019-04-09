from .models import BaseUser2Session, BaseUser
from django.contrib.sessions.models import Session


def one_session_per_user_middleware(get_response):

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if isinstance(request.user, BaseUser):
            current_key = request.session.session_key
            if hasattr(request.user, 'baseuser2session'):
                active_key =  request.user.baseuser2session.session_key
                if active_key != current_key:
                    Session.objects.filter(session_key=active_key).delete()
                    request.user.baseuser2session.session_key = current_key
                    request.user.baseuser2session.save()
            else:
                BaseUser2Session.objects.create(user=request.user, session_key=current_key)

        response = get_response(request)
        # Code to be executed for each request/response after
        # the view is called.


        return response
    return middleware