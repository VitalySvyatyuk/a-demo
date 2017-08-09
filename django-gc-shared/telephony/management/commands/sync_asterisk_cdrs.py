# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from django.core.urlresolvers import reverse

from telephony.models import ExternalAsteriskCDR, CallDetailRecord, VoiceMailCDR
from django.db.models import Max
from django.core.paginator import Paginator
import requests
import gc
from django.conf import settings
from django.core.mail import send_mail





class Command(BaseCommand):
    def execute(self, *args, **options):
        max_external_cdr_id = CallDetailRecord.objects.aggregate(max=Max('external_cdr_id')).get('max', 0) or 0
        new_external_cdrs = ExternalAsteriskCDR.objects.filter(pk__gt=max_external_cdr_id)
        # Paginator for memory optimization!
        paginator = Paginator(new_external_cdrs, 1000)
        for i in paginator.page_range:
            print "Processing page %d" % i
            page = paginator.page(i)
            for external_cdr in page.object_list:
                if not external_cdr.local_cdr:
                    # so, create local CDR for it
                    data = {
                        'recording_file': external_cdr.recordingfile,
                        'call_date': external_cdr.calldate,
                        'duration': external_cdr.duration,
                        'disposition': external_cdr.disposition,
                    }
                    data['number_a'], data['name_a'], data['user_a'] = external_cdr.source_info()
                    data['number_b'], data['name_b'], data['user_b'] = external_cdr.dest_info()

                    cdr, created = CallDetailRecord.objects.get_or_create(
                        external_cdr_id=external_cdr.pk, defaults=data)
                    if created:
                        cdr.save()

                        voice_mail = VoiceMailCDR(cdr=cdr, call_date=cdr.call_date)
                        if voice_mail.get_record_path() is not None:
                            have_voice_mail = requests.head(voice_mail.get_record_path()).status_code == 200
                            if have_voice_mail:
                                voice_mail.recording_file = voice_mail.get_record_path()
                                voice_mail.save()
                                send_mail(
                                    u"New voice mail recieved",
                                    u'Check new voice mail at {}'.format(reverse("admin:telephony_voicemailcdr_change", args=(voice_mail.pk,))),
                                    settings.SERVER_EMAIL,
                                    settings.MANAGERS[0]  # Which means support email
                                )
            gc.collect()
