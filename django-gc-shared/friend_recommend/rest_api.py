# coding=utf-8
from rest_framework import viewsets, status
from rest_framework.decorators import list_route
from rest_framework.response import Response

from friend_recommend.rest_serializers import RecommendationSerializer


class RecommendationViewSet(viewsets.GenericViewSet):
    serializer_class = RecommendationSerializer
    paginator = None

    @list_route(methods=['post'])
    def new_recommendation(self, request):
        serializer = RecommendationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(status=status.HTTP_202_ACCEPTED)
