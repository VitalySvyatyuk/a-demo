from celery.decorators import periodic_task, task
import datetime

from massmail.models import MailingList

@task
def recount_email_count(mailing_list_id):
    m = MailingList.objects.get(pk=mailing_list_id)
    m.subscribers_count = len(m.get_emails())
    m.save()

#@periodic_task(run_every=datetime.timedelta(hours=6))
def recount_all_email_count():
    for m in MailingList.objects.all():
        m.subscribers_count = len(m.get_emails())
        m.save()
