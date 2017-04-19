# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from telephony.models import ExternalAsteriskCDR, CallDetailRecord
from django.db.models import Max
from django.core.paginator import Paginator
import gc

class Command(BaseCommand):
    def execute(self, *args, **options):
        max_external_cdr_id = CallDetailRecord.objects.aggregate(max=Max('external_cdr_id')).get('max', 0) or 0
        new_external_cdrs = ExternalAsteriskCDR.objects.filter(id__gt=max_external_cdr_id)
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
                        external_cdr_id=external_cdr.id, defaults=data)
                    if created:
                        cdr.save()
            gc.collect()
