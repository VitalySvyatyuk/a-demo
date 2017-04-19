# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telephony', '0002_auto_20160202_1855'),
    ]

    operations = [
        migrations.RunSQL("""
            CREATE INDEX telephony_calldetailrecord_number_a_trgm ON telephony_calldetailrecord USING gin (number_a gin_trgm_ops);
            CREATE INDEX telephony_calldetailrecord_number_b_trgm ON telephony_calldetailrecord USING gin (number_b gin_trgm_ops);
        """)
    ]
