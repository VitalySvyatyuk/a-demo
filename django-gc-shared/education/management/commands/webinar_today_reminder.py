# -*- coding: utf-8 -*-

from datetime import date

from django.core.management import BaseCommand

from education.models import WebinarEvent
from notification import models as notification


class Command(BaseCommand):

    """
    Отправляет сообщения пользователям, у которых сегодня начинается вебинар
    """

    def execute(self, *args, **options):
        today = date.today()
        webinars = WebinarEvent.objects.all()

        for webinar in webinars:

            if webinar.starts_at.timetuple()[:3] != today.timetuple()[:3]:
                continue

            regs = webinar.registrations.all()
            mailing_list = [reg.user for reg in regs]

            notification.send(mailing_list, 'webinar_today_reminder',
                              {'event': webinar})
