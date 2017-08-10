# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from django.db.models import Q
import django_filters
from django_filters import Filter
from django import forms
from platforms.types import get_account_type
from datetime import datetime
from django_filters import MethodFilter


class MultipleField(forms.MultipleChoiceField):
    def validate(self, value):
        pass


class MultipleMethodFilter(MethodFilter):
    field_class = MultipleField


class TypesFilter(Filter):
    field_class = MultipleField

    def filter(self, qs, value):
        if value:
            qs = qs.filter(task_type__in=value)
        return qs


class CountriesFilter(Filter):
    field_class = MultipleField

    def filter(self, qs, value):
        if value:
            qs = qs.filter(user__profile__country_pk__in=value)
        return qs


class RegionsFilter(Filter):
    field_class = MultipleField

    def filter(self, qs, value):
        if value:
            qs = qs.filter(user__profile__state_pk__in=value)
        return qs


class LanguagesFilter(Filter):
    field_class = MultipleField

    def filter(self, qs, value):
        if value:
            qs = qs.filter(user__profile__country__language__in=value)
        return qs


class TagFilter(Filter):
    field_class = MultipleField

    def filter(self, qs, value):
        if value:
            # temporary hack, dunno how slow it works
            q = Q()
            for tag in value:
                q &= Q(tags__contains=[tag]) | Q(system_tags__contains=[tag])
            qs = qs.filter(q)
        # qs = qs.filter(Q(tags__overlap=value) | Q(system_tags__overlap=value))
        return qs


class AccountTypeFilter(Filter):
    field_class = MultipleField

    def filter(self, qs, value):
        if value:
            rxs = []
            for v in value:
                t = get_account_type(v)
                if t:
                    rxs.append(t.regex.pattern)
            qs = qs.filter(group_name__regex='|'.join(rxs))
        return qs


class ManagerFilterField(Filter):
    field_class = MultipleField

    def __init__(self, lookup):
        super(ManagerFilterField, self).__init__()
        self.lookup = lookup

    def filter(self, qs, value):
        return qs.filter(self.base_q(self.lookup, value))

    def base_q(self, lookup, value):
        q = Q()
        for id in value:
            if id.startswith('office'):
                oid = id.split('office')[1]
                if oid == 'null':
                    q |= Q(**{lookup+'__crm_manager__office': None})
                else:
                    q |= Q(**{lookup+'__crm_manager__office': oid})
            elif 'null' in id:
                q |= Q(**{lookup: None})
            else:
                q |= Q(**{lookup: id})
        return q


class ManagerFilterMultipleField(ManagerFilterField):
    def filter(self, qs, value):
        return qs.filter(reduce(
            lambda res, lookup: res | self.base_q(lookup, value),
            self.lookup,
            Q()))


class AssigneeFilter(Filter):
    field_class = MultipleField

    def filter(self, qs, value):
        q = Q()
        for id in value:
            if id.startswith('office'):
                oid = id.split('office')[1]
                if oid == 'null':
                    q |= Q(assignee__crm_manager__office=None)
                else:
                    q |= Q(assignee__crm_manager__office=oid)
            elif 'null' in id:
                q |= Q(assignee=None)
            else:
                q |= Q(assignee=id)
        if q:
            qs = qs.filter(q)
        return qs


class DateTimeRangeField(django_filters.fields.RangeField):
    def __init__(self, *args, **kwargs):
        fields = (
            django_filters.fields.IsoDateTimeField(),
            django_filters.fields.IsoDateTimeField())
        super(DateTimeRangeField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            from django.utils import timezone
            tz = timezone.get_current_timezone()
            start_date, stop_date = data_list

            if start_date:
                if not start_date.tzinfo:
                    start_date = start_date.replace(tzinfo=timezone.UTC())
                start_date = start_date.astimezone(tz).replace(microsecond=0)
            if stop_date:
                if not stop_date.tzinfo:
                    stop_date = stop_date.replace(tzinfo=timezone.UTC())
                stop_date = stop_date.astimezone(tz).replace(microsecond=999999)
            return slice(start_date, stop_date)
        return None


class DateTimeFromToRangeFilter(django_filters.DateFromToRangeFilter):
    field_class = DateTimeRangeField


class ResultsFilter(Filter):
    def filter(self, qs, value):
        q = Q()
        if u'null' in value:
            q |= Q(result=None)
        if u'true' in value:
            q |= Q(result=True)
        if u'false' in value:
            q |= Q(result=False)
        if q:
            qs = qs.filter(q)
        return qs


class StatusFilter(Filter):
    def filter(self, qs, value):
        q = Q()
        if u'open' in value:
            q |= Q(closed_at=None)
        if u'closed' in value:
            q |= ~Q(closed_at=None)
        if u'overdue' in value:
            q |= Q(closed_at=None) & Q(deadline__lt=datetime.now())
        if q:
            qs = qs.filter(q)
        return qs


class DispositionFilter(Filter):
    def filter(self, qs, value):
        if value:
            if value == u'answered':
                return qs.answered()
            if value == u'not_answered':
                return qs.not_answered()
        return qs