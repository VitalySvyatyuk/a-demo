# -*- coding: utf-8 -*-
import re
import sys
import urllib
import json
from django.core.management.base import BaseCommand
from geobase.models import City
from geobase.models import Region
from geobase.models import Country

import time

baseUrl = "http://ajax.googleapis.com/ajax/services/language/translate"

def getSplits(text,splitLength=4500):
    ''' Translate Api has a limit on length of text(4500 characters) that can be translated at once, '''
    return (text[index:index+splitLength] for index in xrange(0,len(text),splitLength))

def translate2(text,langpair='ru|en'):
    import urllib

    query = urllib.urlencode({'q' : text.encode("utf-8"),'langpair':langpair})
    url = u'http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&%s'.encode("utf-8") \
      % (query)
    search_results = urllib.urlopen(url)
    json = json.loads(search_results.read())
    if json == None:
        mess = ''
    else:
        if json['responseData'] == None:
            mess = ''
        else:
            mess = json['responseData']['translatedText']
    return mess

class Command(BaseCommand):

      def handle(self, *args, **options):
          #self.translate_region()
          #self.translate_country()
          #self.translate_city()
          #self.translate_city_range()
          pass


      def translate_region(self):
          regions = Region.objects.filter(name_en="")
          for region in regions:
              en_name = translate2(region.name)
              en_name = en_name.replace('#39;',"'")
              if en_name == "":
                  return 
              region.name_en = en_name
              region.save()
              #time.sleep(2)

      def translate_country(self):
          countries = Country.objects.filter(name_en="")
          for country in countries:
              en_name = translate2(country.name)
              en_name = en_name.replace('#39;',"'")
              if en_name == "":
                  return
              country.name_en = en_name
              country.save()
              #time.sleep(2)

      def translate_city(self):
          for i in xrange(10):
              cities = City.objects.filter(name_en="")
              for city in cities:
                  en_name = translate2(city.name)
                  en_name = en_name.replace('#39;',"'")
                  if en_name == "":
                      break
                  city.name_en = en_name
                  city.save()
              time.sleep(300)

      def translate_city_range(self):
          for i in xrange(55):
              cities = City.objects.filter(name_en="")[1:20]
              cities_ru = list()
              for city in cities:
                  cities_ru.append(city.name)
              cities_en = translate2('|'.join(cities_ru)).split('|')
              city_dict = dict(zip(cities_ru, cities_en))
              for city in cities:
                  city.name_en = city_dict[city.name]
                  city.save()
              time.sleep(10)
