import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from scratch_api.models import Production
from django.utils.encoding import escape_uri_path



def download_by_id(request, production_id):
    production = get_object_or_404(Production, pk=production_id)
    file_path = production.file.path
    if os.path.exists(file_path):
         with open(file_path, 'rb') as fh:
             response = HttpResponse(fh.read(), content_type="application/octet-stream")
             # Ref https://segmentfault.com/q/1010000009078463
             # make chinese works fine
             response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(os.path.basename(file_path)))
             return response
    raise Http404