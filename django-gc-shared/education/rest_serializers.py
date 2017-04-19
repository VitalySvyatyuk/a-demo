# -*- coding: utf-8 -*-

from rest_framework import serializers

from education.models import WebinarRegistration


class WebinarRegistrationSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()

    link_to_room = serializers.ReadOnlyField(source='tutorial.link_to_room')
    record = serializers.ReadOnlyField(source='tutorial.youtube_video_url')

    starts_at = serializers.ReadOnlyField(source='tutorial.starts_at')
    name = serializers.ReadOnlyField(source='tutorial.webinar.name')
    category = serializers.ReadOnlyField(source='tutorial.webinar.category')
    category_display = serializers.ReadOnlyField(source='tutorial.webinar.get_category_display')

    class Meta:
        model = WebinarRegistration

        fields = (
            'id',
            'starts_at',
            'status',

            'link_to_room',
            'record',

            'name',
            'category',
            'category_display')
