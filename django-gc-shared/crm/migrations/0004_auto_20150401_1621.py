# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_personalmanager_can_request_new_customers'),
    ]

    operations = [
        migrations.RunSQL(
            """CREATE OR REPLACE FUNCTION custom_regex_sort(anyarray varchar[], anyelement)
               RETURNS INT AS
               $$
               SELECT i FROM (
               SELECT generate_series(array_lower($1,1),array_upper($1,1))
               ) g(i)
               WHERE $2 ~ $1[i]
               LIMIT 1;
               $$ LANGUAGE SQL IMMUTABLE;""",
            reverse_sql="DROP FUNCTION custom_regex_sort(anyarray varchar[], anyelement)",
        )
    ]
