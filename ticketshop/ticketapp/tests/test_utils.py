from datetime import datetime, date
from unittest import TestCase
from ..utils import daterange

class DaterangeTest(TestCase):
    """
    Tests the daterange function
    """
    def testOneDayRange(self):
        """
        Test a range from one day to the same.
        """
        day = datetime.now()
        self.assertEqual([day.date()], list(daterange(day,day)))

    def testTwoDays(self):
        day1 = date(2013,01,03)
        day2 = date(2013,01,04)
        self.assertEqual([day1,day2], list(daterange(day1, day2)))

    def testMore(self):
        days = [ date(2013,01,d) for d in range(4,19) ]
        self.assertEqual( days, list(daterange(days[0], days[-1])) )
