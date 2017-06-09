# -*- coding: utf-8 -*-

import sys
import traceback
from uuid import uuid4

from celery.app import default_app
from celery.task import task
from django.conf import settings
from django.core.mail import mail_admins
from django.template import loader
from django.utils import translation
from djcelery.backends.database import DatabaseBackend

from platforms.mt4.api.database import DatabaseAPI
from platforms.models import TradingAccount
from notification import models as notification


@task(backend=DatabaseBackend(default_app), acks_late=True, track_started=True, queue="reports")
def generate_report(context, template, decimal_separator, saved_report, language, user):
    translation.activate(language)

    if context.get('account'):
        if isinstance(context['account'], int):
            context['account'] = TradingAccount(mt4_id=context['account'])
        api = context['account'].get_api("db")
    else:
        api = DatabaseAPI()

    try:
        context['report'] = getattr(api, context['report_type'])(user=user, **context)
    except Exception: #Some error happened. We should at least notify user and admins and delete the report.
        e = sys.exc_info()
        notification.send([saved_report.for_user], 'report_generation_failed',
            extra_context={'name': saved_report.name})
        mail_admins(u"Report generation FAILED", u"Generation of report %s for user \
            ID=%d FAILED. Celery task id: %s\n%s: %s\nTraceback\n%s" % (saved_report.name,
                                                 saved_report.for_user.pk,
                                                 saved_report.celery_task_id,
                                                 e[0], e[1],
                                                 ''.join(traceback.format_list( traceback.extract_tb(e[2]) )) ))
        saved_report.delete()
        raise
    context['DECIMAL_SEPARATOR'] = decimal_separator
    context["STATIC_URL"] = "/static/"
    result_html = loader.render_to_string(template_name=template, dictionary=context)
    filename = str(uuid4()) + ".html"
    outfile = open(settings.SAVED_REPORTS_PATH + filename, 'w')
    outfile.write(result_html.encode('utf-8'))
    outfile.close()
    saved_report.filename = filename
    saved_report.save()
    notification.send([saved_report.for_user], 'report_has_been_generated',
                     extra_context={'name': saved_report.name,
                                    'report_id': saved_report.pk})
    return {'result': saved_report}