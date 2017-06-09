# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import shared.utils
import project.validators


class Migration(migrations.Migration):

    dependencies = [
        ('issuetracker', '0010_auto_20170320_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issueattachment',
            name='file',
            field=models.FileField(help_text='Supported extensions: doc, docx, bmp, gif, jpg, jpeg, png, pdf, xls, xlsx. Filesize limit: 5.00 Mb', upload_to=shared.utils.UploadTo(b'issue_attachments'), verbose_name='Attachment', validators=[project.validators.allow_file_extensions((b'doc', b'docx', b'bmp', b'gif', b'jpg', b'jpeg', b'png', b'pdf', b'xls', b'xlsx')), project.validators.allow_file_size(5242880)]),
        ),
    ]
