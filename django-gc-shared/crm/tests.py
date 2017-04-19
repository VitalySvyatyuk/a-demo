import sys
import os

# init Django evironment
sys.path = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")] + sys.path
sys.path = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../django-shared")] + sys.path
sys.path = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../django-gc-shared")] + sys.path
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import unittest
import warnings

warnings.simplefilter("ignore")  # ignore all warnings, for pretty output


class TestCalculateTaskFinishTime(unittest.TestCase):
    def test_worktime_end(self):
        from crm.utils import calculate_finish_time
        from datetime import datetime, time
        now = datetime(2014, 11, 18, 15, 36, 0)

        class MockCRMManager(object):
            worktime_start = time(9, 0, 0)
            worktime_end = time(16, 0, 0)

        class MockUser(object):
            crm_manager = MockCRMManager()

        self.assertEqual(
            calculate_finish_time(MockUser(), now=now),
            datetime(2014, 11, 18, 23, 59, 59)
        )

    def test_worktime_end_to_next_day(self):
        from crm.utils import calculate_finish_time
        from datetime import datetime, time
        now = datetime(2014, 11, 18, 16, 36, 0)

        class MockCRMManager(object):
            worktime_start = time(9, 0, 0)
            worktime_end = time(16, 0, 0)

        class MockUser(object):
            crm_manager = MockCRMManager()

        self.assertEqual(
            calculate_finish_time(MockUser(), now=now),
            datetime(2014, 11, 19, 23, 59, 59)
        )

    def test_worktime_end_with_at_time(self):
        from crm.utils import calculate_finish_time
        from datetime import datetime, time, timedelta
        now = datetime(2014, 11, 18, 12, 30, 0)

        class MockCRMManager(object):
            worktime_start = time(9, 0, 0)
            worktime_end = time(15, 0, 0)

        class MockUser(object):
            crm_manager = MockCRMManager()

        self.assertEqual(
            calculate_finish_time(MockUser(), timedelta(minutes=20), now=now),
            datetime(2014, 11, 18, 12, 50, 0)
        )

    def test_worktime_end_with_at_time_next_day(self):
        from crm.utils import calculate_finish_time
        from datetime import datetime, time, timedelta
        now = datetime(2014, 11, 18, 14, 46, 0)

        class MockCRMManager(object):
            worktime_start = time(9, 0, 0)
            worktime_end = time(15, 0, 0)

        class MockUser(object):
            crm_manager = MockCRMManager()

        self.assertEqual(
            calculate_finish_time(MockUser(), timedelta(minutes=20), now=now),
            datetime(2014, 11, 19, 23, 59, 59)
        )

    def test_bug1(self):
        from crm.utils import calculate_finish_time
        from datetime import datetime, time, timedelta
        now = datetime(2014, 12, 7, 9, 4, 0)

        class MockCRMManager(object):
            worktime_start = time(9, 0, 0)
            worktime_end = time(15, 0, 0)

        class MockUser(object):
            crm_manager = MockCRMManager()

        self.assertEqual(
            calculate_finish_time(
                MockUser(),
                timedelta(minutes=20),
                now=now,
                force_time=time(23, 59, 59)),
            datetime(2014, 12, 8, 23, 59, 59)
        )

    def test_bug2(self):
        from crm.utils import calculate_finish_time
        from datetime import datetime, time
        now = datetime(2014, 12, 10, 23, 50, 0)

        class MockCRMManager(object):
            worktime_start = time(9, 0, 0)
            worktime_end = time(15, 0, 0)

        class MockUser(object):
            crm_manager = MockCRMManager()

        self.assertEqual(
            calculate_finish_time(
                MockUser(),
                now=now),
            datetime(2014, 12, 11, 23, 59, 59)
        )


if __name__ == '__main__':
    unittest.main()
