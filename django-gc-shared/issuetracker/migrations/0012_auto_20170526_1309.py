# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import shared.utils
import project.validators


class Migration(migrations.Migration):

    dependencies = [
        ('issuetracker', '0011_auto_20170523_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issueattachment',
            name='file',
            field=models.FileField(help_text='\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u043c\u044b\u0435 \u0440\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u0438\u044f: doc, docx, bmp, gif, jpg, jpeg, png, pdf, xls, xlsx. \u041c\u0430\u043a\u0441. \u043e\u0431\u044a\u0435\u043c \u0444\u0430\u0439\u043b\u0430: 5.00 \u041c\u0411', upload_to=shared.utils.UploadTo(b'issue_attachments'), verbose_name='Attachment', validators=[project.validators.allow_file_extensions((b'doc', b'docx', b'bmp', b'gif', b'jpg', b'jpeg', b'png', b'pdf', b'xls', b'xlsx')), project.validators.allow_file_size(5242880)]),
        ),
    ]
