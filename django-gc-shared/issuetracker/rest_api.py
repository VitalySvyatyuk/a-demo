# coding=utf-8
from rest_framework import viewsets, mixins
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser

from issuetracker.models import UserIssue, IssueComment, GenericIssue
from issuetracker.rest_serializers import UserIssueSerializer, IssueCommentSerializer


class UserIssueViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = UserIssueSerializer
    parser_classes = (FormParser, MultiPartParser, JSONParser)
    paginator = None

    def get_queryset(self):
        return UserIssue.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IssueCommentViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = IssueCommentSerializer
    parser_classes = (FormParser, MultiPartParser, JSONParser)
    paginator = None

    def get_queryset(self):
        return IssueComment.objects.filter(
            issue__author=self.request.user,
            issue=self.kwargs['issue_id']).order_by('id')

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            issue=GenericIssue.objects.get(author=self.request.user, id=self.kwargs['issue_id'])
        )
