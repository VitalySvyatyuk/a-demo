import json
from datetime import datetime, date, time, timedelta
import time


class JSEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime) or isinstance(obj, date):
            return time.mktime(obj.timetuple())*1000
        else:
            return json.JSONEncoder.default(self, obj)