# -*- coding: utf-8 -*-

from rest_framework import pagination


class CustomPaginationSerializer(pagination.PageNumberPagination):
    results_field = 'results'
    page_size = 20
    page_size_query_param = 'per_page'
    max_page_size = 1000

    def paginate_queryset(self, queryset, request, view=None):
        self.view = view
        return super(CustomPaginationSerializer, self).paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
        from rest_framework.response import Response
        payload = {
            'num_pages': self.page.paginator.num_pages,
            'page': self.page.number,
            'count': self.page.paginator.count,
            'results': data,
        }
        if getattr(self.view, 'get_queryset_summary', None):
            payload['summary'] = self.view.get_queryset_summary()
        return Response(payload)
