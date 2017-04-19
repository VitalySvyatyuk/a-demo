# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import shared.utils
import project.validators
import jsonfield.fields
import django.contrib.postgres.fields
from django.conf import settings
import geobase.phone_code_widget


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('geobase', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDataValidation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=50, verbose_name='Parameter')),
                ('is_valid', models.NullBooleanField(verbose_name='Is the data valid?')),
                ('comment', models.CharField(max_length=160, null=True, verbose_name='Manager comment', blank=True)),
                ('user', models.ForeignKey(related_name='validations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Document name', choices=[(b'passport_scan', 'Identity document'), (b'driver_license', 'Driver license'), (b'birth_certificate', 'Certificate of birth'), (b'real_ib_agreement', 'Real IB agreement'), (b'other', 'Other document')])),
                ('description', models.TextField(null=True, verbose_name='Document description', blank=True)),
                ('file', models.FileField(help_text='Supported extensions: %(ext)s. Filesize limit: %(limit)s Mb', upload_to=shared.utils.UploadTo(b'files'), verbose_name='File', validators=[project.validators.allow_file_extensions((b'doc', b'docx', b'bmp', b'gif', b'jpg', b'jpeg', b'png', b'pdf')), project.validators.allow_file_size(5242880)])),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='Creation timestamp')),
                ('is_deleted', models.BooleanField(default=False, verbose_name=b'Document is deleted')),
                ('fields', jsonfield.fields.JSONField(null=True, verbose_name='Document fields', blank=True)),
                ('user', models.ForeignKey(related_name='documents', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('middle_name', models.CharField(max_length=45, null=True, verbose_name='Middle name', blank=True)),
                ('birthday', models.DateField(null=True, verbose_name='Birthday', blank=True)),
                ('city', models.CharField(help_text='The city where you live', max_length=100, null=True, verbose_name='City', blank=True)),
                ('address', models.CharField(help_text='Example: pr. Stachek, 8A', max_length=80, null=True, verbose_name='Address', blank=True)),
                ('skype', models.CharField(help_text='Example: gc_clients', max_length=80, null=True, verbose_name='Skype', blank=True)),
                ('icq', models.CharField(help_text='Example: 629301132', max_length=20, null=True, verbose_name='ICQ', blank=True)),
                ('phone_home', geobase.phone_code_widget.CountryPhoneCodeField(max_length=40, blank=True, help_text='Example: 8-800-333-1003', null=True, verbose_name='Home phone', db_index=True)),
                ('phone_work', geobase.phone_code_widget.CountryPhoneCodeField(max_length=40, blank=True, help_text='Example: +7 (812) 300-81-96', null=True, verbose_name='Work phone', db_index=True)),
                ('phone_mobile', geobase.phone_code_widget.CountryPhoneCodeField(max_length=40, blank=True, help_text='Example: +7 (911) 200-19-55', null=True, verbose_name='Mobile phone', db_index=True)),
                ('avatar', models.ImageField(help_text='Your photo', upload_to=shared.utils.UploadTo(b'userfiles/avatars'), null=True, verbose_name='Avatar', blank=True)),
                ('social_security', models.CharField(max_length=50, null=True, verbose_name='Social security number', blank=True)),
                ('tin', models.CharField(help_text='Tax identification number', max_length=50, null=True, verbose_name='TIN', blank=True)),
                ('manager_auto_assigned', models.BooleanField(default=True, verbose_name='\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043d\u0430\u0437\u043d\u0430\u0447\u0435\u043d \u0430\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438')),
                ('assigned_to_current_manager_at', models.DateTimeField(null=True, verbose_name='Assigned to manager at', blank=True)),
                ('language', models.CharField(blank=True, max_length=20, null=True, choices=[(b'ru', b'Russian'), (b'en', b'English')])),
                ('agent_code', models.PositiveIntegerField(help_text="If you don't know what it is, leave empty", null=True, verbose_name='Agent code', blank=True)),
                ('lost_otp', models.BooleanField(default=False, verbose_name='Did user lose his OTP')),
                ('auth_scheme', models.CharField(max_length=10, null=True, verbose_name=b'Auth scheme', choices=[(b'otp', b'OTP auth'), (b'sms', b'SMS auth'), (b'voice', b'Voice auth')])),
                ('params', jsonfield.fields.JSONField(default={}, null=True, verbose_name='Details', blank=True)),
                ('user_from', jsonfield.fields.JSONField(default={}, null=True, verbose_name='Source', blank=True)),
                ('registered_from', models.CharField(default=b'', max_length=255, verbose_name='Registered from', blank=True)),
                ('last_activity_ts', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), verbose_name=b'Last activity', db_index=True)),
                ('last_activities', django.contrib.postgres.fields.ArrayField(default=list, base_field=models.CharField(max_length=255), verbose_name=b'Last activities', size=None)),
                ('country', models.ForeignKey(blank=True, to='geobase.Country', help_text='Example: Russia', null=True, verbose_name='Country')),
                ('manager', models.ForeignKey(related_name='managed_profiles', verbose_name='\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043f\u043e \u0442\u043e\u0440\u0433\u043e\u0432\u043b\u0435', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('state', models.ForeignKey(verbose_name='State / Province', blank=True, to='geobase.Region', null=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User profile',
                'verbose_name_plural': 'User profiles',
            },
        ),
        migrations.AlterUniqueTogether(
            name='userdatavalidation',
            unique_together=set([('user', 'key')]),
        ),
    ]
