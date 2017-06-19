# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import shared.utils
import project.validators


class Migration(migrations.Migration):

    dependencies = [
        ('uptrader_cms', '0012_auto_20170307_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='legaldocument',
            name='file',
            field=models.FileField(help_text='Supported extensions: doc, docx, bmp, gif, jpg, jpeg, png, pdf, xls, xlsx. Filesize limit: 15.00 Mb', upload_to=shared.utils.UploadTo(b'legal_documents'), verbose_name='File', validators=[project.validators.allow_file_extensions((b'doc', b'docx', b'bmp', b'gif', b'jpg', b'jpeg', b'png', b'pdf', b'xls', b'xlsx')), project.validators.allow_file_size(15728640)]),
        ),
    ]
