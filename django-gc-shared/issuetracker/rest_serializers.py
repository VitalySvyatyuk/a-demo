# -*- coding: utf-8 -*-
import imghdr
import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group

from django.core.mail import send_mail

from rest_framework import serializers

from issuetracker.models import UserIssue, IssueComment, IssueAttachment
from project.rest_fields import ExtraMetadataSlugRelatedField
from project.models import GROUP_NAMES

ALLOWED_GROUPS = (
    ('Back office_1', _("Common question")),  # Back office  (common question)
    ('Dealing room_1', _("Technical question"),),  # Dealing room (technical question)
    ('Back office_2', _("Financial question")),  # Back office (financial question)
)
ALLOWED_GROUPS_NAMES = ('Dealing room', 'Back office')


class IssueAttachmentSerializer(serializers.ModelSerializer):
    size = serializers.ReadOnlyField(source='file.size')
    url = serializers.ReadOnlyField(source='file.url')
    is_image = serializers.SerializerMethodField()

    def get_is_image(self, obj):
        return bool(imghdr.what(obj.file))

    class Meta:
        model = IssueAttachment
        fields = (
            'id',
            'file',
            'url',
            'size',
            'is_image'
        )
        read_only_fields = (
            'id',
        )


class UserIssueSerializer(serializers.ModelSerializer):
    status_display = serializers.ReadOnlyField(source='get_status_display')
    files = serializers.ListField(
        write_only=True,
        child=serializers.FileField(
            label=_("Attachments"),
            help_text=IssueAttachment.FILE_HELP_TEXT
        )
    )
    attachments = IssueAttachmentSerializer(many=True, read_only=True)

    department = ExtraMetadataSlugRelatedField(
        label=_("Department"),
        slug_field="name",
        extra_metadata={
            "choices": [{
                "display_name": display,
                "value": name
            } for name, display in ALLOWED_GROUPS]
        },
        queryset=Group.objects.all()
    )

    def validate_department(self, value):
        if value and value.name not in ALLOWED_GROUPS_NAMES:
            raise serializers.ValidationError(_("Invalid value"))
        return value

    def validate_files(self, value):
        for file in value:
            serializer = IssueAttachmentSerializer(data={
                'file': file
            })
            serializer.is_valid(raise_exception=True)
        return value

    def create(self, validated_data):
        files = validated_data.pop('files')
        issue = super(UserIssueSerializer, self).create(validated_data)
        for file in files:
            attach = IssueAttachment()
            attach.user = validated_data['author']
            attach.issue = issue
            attach.file = file
            attach.save()

        send_mail(
            u"User {} created issue".format(validated_data['author']),
            u'link: https://arumcapital.eu/my/admin/issuetracker/genericissue/{}/'.format(issue.id),
            settings.SERVER_EMAIL,
            settings.MANAGERS[0]  # Which means support email
        )

        return issue

    class Meta:
        model = UserIssue
        fields = (
            'id',
            'status',
            'status_display',

            'department',
            'title',
            'text',

            'attachments',
            'files',

            'creation_ts',
            'update_ts',
            'deadline',
        )
        read_only_fields = (
            'id',
            'status',

            'creation_ts',
            'update_ts',
            'deadline',
        )


class IssueCommentSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        write_only=True,
        child=serializers.FileField(
            label=_("Attachments"),
            help_text=IssueAttachment.FILE_HELP_TEXT
        )
    )

    def validate_files(self, value):
        for file in value:
            serializer = IssueAttachmentSerializer(data={
                'file': file
            })
            serializer.is_valid(raise_exception=True)
        return value

    def create(self, validated_data):
        for file in validated_data.pop('files'):
            attach = IssueAttachment()
            attach.user = validated_data['user']
            attach.issue = validated_data['issue']
            attach.file = file
            attach.save()

        return super(IssueCommentSerializer, self).create(validated_data)

    class Meta:
        model = IssueComment
        fields = (
            'id',
            'user',
            'issue',

            'text',
            'files',

            'creation_ts',
        )
        read_only_fields = (
            'id',
            'user',
            'issue',

            'creation_ts',
        )
