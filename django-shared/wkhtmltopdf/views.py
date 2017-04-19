import os

from django.http import HttpResponse

from models import render_to_pdf

def render_template(request, template_name, filename=None):
    tempfile = render_to_pdf(template_name)
    content = open(tempfile).read()
    os.remove(tempfile)
    response = HttpResponse(content, content_type="application/pdf")
    if filename:
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response