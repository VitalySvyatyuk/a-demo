# -*- coding: UTF-8 -*-

import re
from datetime import datetime

import requests
from BeautifulSoup import BeautifulSoup
from dateutil.parser import parser
from django.core.management import BaseCommand
from pytz import timezone

from uptrader_cms.models import IndicatorCountry, Indicator, IndicatorEvent


class Command(BaseCommand):
    @staticmethod
    def create_calendar_event(ru, en, zh):
        event_name_ru = ru.get(u'text', '').replace('&nbsp;', '')
        if event_name_ru.find(u"Количество чистых спекулятивных позиций по") != -1:
            return
        country_code = ru.get(u'country', None)
        event_name_en = en.get(u'text', '').replace('&nbsp;', '')
        event_name_zh = zh.get(u'text', '').replace('&nbsp;', '')
        event_id = ru.get(u'id', '')
        event_previous = en.get(u'previous', None)
        event_forecast = en.get(u'forecast', None)
        event_fact = en.get(u'actual', None)
        event_volatility = ru.get(u'volatility', None)
        event_time = en.get(u'date', None)

        if country_code:
            country_code = country_code.lower().strip()
            # Fix for European Monetary Union events
            if country_code == u'emu':
                country_code = u'eu'

        indicator_country = IndicatorCountry.objects.filter(
            code=country_code).first()

        event_indicator = Indicator.objects.filter(
            country=indicator_country,
            fxstreet_id=event_id
        ).first()

        if event_indicator is None:
            event_indicator = Indicator.objects.create(
                country=indicator_country,
                name_en=event_name_en,
                name_ru=event_name_ru,
                # name_zh_cn=event_name_zh,
                name=event_name_en,
                fxstreet_id=event_id
            )

        event_title = u'{} {}'.format(event_name_ru, event_time)

        event_values = {
            'previous': event_previous,
            'forecast': event_forecast,
            'facts': event_fact,
            'event_date': event_time,
            'title': event_title
        }
        qs = IndicatorEvent.objects.filter(
            importance=event_volatility,
            indicator=event_indicator,
            event_date=event_time
        )

        if qs.exists():
            qs.update(**event_values)
        else:
            IndicatorEvent.objects.create(
                importance=event_volatility,
                indicator=event_indicator,
                **event_values
            )

    @staticmethod
    def get_request_config(lang='ru'):
        base_request_config_new = {
            'columns': 'exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous',
            'countries': '25,4,17,72,6,37,43,5,22,12,110,35',
            'timeZone': '18',  # Russian Standard Time
            'lang': '7',  # Language codes: 1-English, 6-Chinese, 7-Russian
            'calType': 'week'
        }

        if lang == 'ru':
            return base_request_config_new
        elif lang == 'en':
            # Change request_params for second request (needed to get english indicator name)
            base_request_config_new['lang'] = '1'
            return base_request_config_new
        elif lang == 'zh-cn':
            base_request_config_new['lang'] = '6'
            return base_request_config_new

    @staticmethod
    def parse_datetime(date_text):
        utc = timezone('UTC')
        tz = timezone('Europe/Moscow')

        time_parser = parser()

        return time_parser.parse(
            date_text
        ).replace(tzinfo=utc).astimezone(tz=tz)

    @staticmethod
    def parse_calendar(response_text):
        class_to_code = {
            'Australia': 'au',
            'United_Kingdom': 'uk',
            'Germany': 'de',
            'Europe': 'eu',
            'Canada': 'ca',
            'China': 'cn',
            'New_Zealand': 'nz',
            'United_States': 'us',
            'France': 'fr',
            'Switzerland': 'ch',
            'South_Africa': 'za',
            'Japan': 'jp'
        }

        soup = BeautifulSoup(response_text)

        table_body = soup.find('table', id="ecEventsTable").find('tbody')
        event_list = []
        current_date = ''
        for tr in table_body.findAll('tr'):
            tr_id = tr.get('id')
            if tr_id and re.match(r'eventRowId_.*', tr.get('id')):
                event_id = tr.get('id').split('_')[1]
                country_class = tr.find('td', attrs={'class': 'flagCur'}).span.get('class').split()[1]
                event_td = tr.find('td', attrs={'class': re.compile(r'.* event')})
                volatility_td = tr.find('td', 'sentiment')

                previous_td = tr.find('td', id='eventPrevious_'+event_id)
                forecast_td = tr.find('td', id='eventForecast_'+event_id)
                actual_td = tr.find('td', id='eventActual_'+event_id)
                date_text = tr.get('event_timestamp') or current_date
                event = {
                    'id': event_id,
                    'date': Command.parse_datetime(date_text),
                    'country': class_to_code.get(country_class),
                    'text': event_td.text,
                    'previous': previous_td.text if previous_td else None,
                    'forecast': forecast_td.text if forecast_td else None,
                    'actual': actual_td.text if actual_td else None,
                    'volatility': len(volatility_td.findAll(
                        'i',
                        attrs={
                            'class': re.compile(r'\w+ grayFullBullishIcon \w+')
                        }))
                }
                event_list.append(event)
            elif not tr_id:
                current_date_ts = re.sub(r'[A-Za-z]+', '', tr.td.get('id'))
                current_date = unicode(datetime.fromtimestamp(float(current_date_ts)))
        return event_list

    def handle(self, *args, **options):
        calendar_request_url = "http://ec.forexprostools.com/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:49.0) "
                                 "Gecko/20100101 Firefox/49.0"}

        ru_response = requests.get(calendar_request_url, headers=headers,
                                   params=self.get_request_config('ru'))
        # English and chinese data is needed for adding translation to event names
        en_response = requests.get(calendar_request_url, headers=headers,
                                   params=self.get_request_config('en'))
        zh_response = requests.get(calendar_request_url, headers=headers,
                                   params=self.get_request_config('zh-cn'))

        if ru_response.status_code != 200 or en_response.status_code != 200 or zh_response.status_code != 200:
            return

        ru_data = self.parse_calendar(ru_response.text)
        en_data = self.parse_calendar(en_response.text)
        zh_data = self.parse_calendar(zh_response.text)

        ru_dict = {e['id']: e for e in ru_data}
        en_dict = {e['id']: e for e in en_data}
        zh_dict = {e['id']: e for e in zh_data}

        zipped_list = [(ru_dict[k], en_dict[k], zh_dict[k]) for k in set(ru_dict.keys()) & set(en_dict.keys()) & set(zh_dict.keys())]

        for item in zipped_list:
            self.create_calendar_event(*item)

        # Clear removed events
        dates_list = [ev['date'] for ev in en_data]

        IndicatorEvent.objects.filter(
            event_date__range=[min(dates_list), max(dates_list)]
        ).exclude(
            indicator__fxstreet_id__in=ru_dict.keys()
        ).delete()
