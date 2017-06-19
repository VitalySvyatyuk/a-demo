# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import uptrader_cms.models
import shared.utils
import project.validators


class Migration(migrations.Migration):

    dependencies = [
        ('uptrader_cms', '0002_companynews_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegalDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Document name')),
                ('name_ru', models.CharField(max_length=100, null=True, verbose_name='Document name')),
                ('name_en', models.CharField(max_length=100, null=True, verbose_name='Document name')),
                ('category', models.CharField(max_length=100, verbose_name='Category', choices=[(b'docs', 'Documentation'), (b'policy', 'Non-disclosure policy'), (b'risks', 'Risk warning'), (b'regulation', 'Regulation'), (b'cookies', 'Cookies information')])),
                ('languages', django.contrib.postgres.fields.ArrayField(default=uptrader_cms.models.docs_default_languages, base_field=models.CharField(max_length=10), size=None)),
                ('file', models.FileField(help_text='\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u043c\u044b\u0435 \u0440\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u0438\u044f: doc, docx, bmp, gif, jpg, jpeg, png, pdf, xls, xlsx. \u041c\u0430\u043a\u0441. \u043e\u0431\u044a\u0435\u043c \u0444\u0430\u0439\u043b\u0430: 15.00 \u041c\u0411', upload_to=shared.utils.UploadTo(b'legal_documents'), verbose_name='File', validators=[project.validators.allow_file_extensions((b'doc', b'docx', b'bmp', b'gif', b'jpg', b'jpeg', b'png', b'pdf', b'xls', b'xlsx')), project.validators.allow_file_size(15728640)])),
            ],
            options={
                'verbose_name': 'Legal document',
                'verbose_name_plural': 'Legal documents',
            },
        ),
    ]
