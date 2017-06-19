

class TimeDeltaWithWeekends(object):

    def __init__(self, **kwargs):
        # Now supports only days
        if 'days' not in kwargs.keys():
            raise ValueError('Please specify amount of days')

        self._days = kwargs.pop('days')






  