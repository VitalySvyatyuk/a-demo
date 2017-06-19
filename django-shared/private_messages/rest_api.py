# coding=utf-8
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from private_messages.rest_serializers import MessageSerializer
from private_messages.models import Message, inbox_count_for


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(
            recipient=self.request.user,
            recipient_deleted_at__isnull=True)

    @list_route()
    def inbox_count(self, request):
        return Response(inbox_count_for(request.user))

    @list_route()
    def last_unread(self, request):
        last_message = self.get_queryset().filter(read_at__isnull=True).first()
        if last_message:
            return Response(self.serializer_class(last_message).data)
        return Response()

    @list_route(methods=['post'])
    def batch_mark(self, request):
        status = request.data['status']
        assert status in ['deleted', 'read', 'unread']
        if status == 'deleted':
            for msg in self.get_queryset().filter(id__in=request.data['id']):
                msg.mark_deleted(request.user)

        elif status == 'read':
            for msg in self.get_queryset().filter(id__in=request.data['id']):
                msg.mark_read()

        elif status == 'unread':
            for msg in self.get_queryset().filter(id__in=request.data['id']):
                msg.mark_unread()
        return Response()
