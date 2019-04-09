from django.conf.urls import include, url

from OJ.views import Website_ProblemList, ProblemDetail
from util.views import download_by_id
from . import views

app_name = 'utils'


urlpatterns = [
    url(r'^download_production/(?P<production_id>.+)/$', download_by_id),

]