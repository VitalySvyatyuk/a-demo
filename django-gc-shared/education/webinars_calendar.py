# -*- coding: utf-8 -*-

import datetime
from calendar import Calendar
from itertools import groupby

import pytz
from pytz.exceptions import UnknownTimeZoneError
from dateutil.relativedelta import relativedelta


class WebinarsCalendar(Calendar):

    def __init__(self, year, month, events, tz="Europe/Moscow", *args, **kwargs):

        super(WebinarsCalendar, self).__init__(*args, **kwargs)

        self.year = year
        self.month = month
        try:
            self.tz = pytz.timezone(tz)
        except UnknownTimeZoneError:
            self.tz = pytz.timezone("Europe/Moscow")
        local_tz = pytz.timezone("Europe/Moscow")

        self.events = {
            k: list(v)
            for k, v in groupby(events, lambda x: self.tz.normalize(local_tz.localize(x.starts_at)).date().day)
        }

    def weeks(self):
        return self.monthdays2calendar(self.year, self.month)

    def week_days(self):
        return self.iterweekdays()

    def get_week_events(self, week):
        return [(day, week_day, self.events[day]) for day, week_day in week if day in self.events]

    def get_day_events(self, day):
        return self.events.get(day, [])

    def itermonthdays2(self, year, month):
        """
        Like itermonthdates(), but will yield (day number, weekday number)
        tuples. For days outside the specified month the day number is 0.
        """
        for date in self.itermonthdates(year, month):
            if date.month != month:
                yield (0, date.weekday(), None)
            else:
                yield (date.day, date.weekday(), datetime.date(year, month, date.day))

    def get_relative_date(self, months=1):
        d = datetime.date(self.year, self.month, 1)
        date = d + relativedelta(months=months)
        return {
            "month": date.month,
            "year": date.year
        }

    def next_month(self):
        return self.get_relative_date(months=1)

    def previous_month(self):
        return self.get_relative_date(months=-1)
