from __future__ import absolute_import, division, print_function

import datetime

import pytest

from dateutil.parser import parse
from dateutil.rrule import DAILY, FR, MO, SU, TH, TU, WE, rrule, rruleset

from business_calendar import FOLLOWING, MODIFIEDFOLLOWING, PREVIOUS, Calendar


_HOLIDAYS = [
    parse(holiday)
    for holiday in """
Friday Jan 1, 2010
Friday Apr 2, 2010
Monday May 3, 2010
Monday May 31, 2010
Saturday Dec 25, 2010
Sunday Dec 26, 2010
Monday Dec 27, 2010
Tuesday Dec 28, 2010
Dec 28, 2010
Dec 28, 2010
Dec 28, 2010
Saturday Jan 1, 2011
Monday Jan 3, 2011
Friday Apr 22, 2011
Friday Apr 29, 2011
Monday May 2, 2011
May 3, 2011
May 4, 2011
May 5, 2011
May 6, 2011
Monday May 30, 2011
Sunday Dec 25, 2011
Monday Dec 26, 2011
Tuesday Dec 27, 2011
Sunday Jan 1, 2012
Monday Jan 2, 2012
Friday Apr 6, 2012
Monday May 7, 2012
Monday Jun 4, 2012
Tuesday Jun 5, 2012
Jun 6, 2012
Jun 7, 2012
Jun 8, 2012
Jun 9, 2012
Jun 10, 2012
Jun 11, 2012
Tuesday Dec 25, 2012
Wednesday Dec 26, 2012
Tuesday Jan 1, 2013
Friday Mar 29, 2013
Monday May 6, 2013
Monday May 27, 2013
Wednesday Dec 25, 2013
Thursday Dec 26, 2013
""".strip().split(
        "\n"
    )
]


def create_calendar_test_data(calendar_workdays, dateutil_workdays, holidays):
    """Creates calendar and generates list of dates using `dateutil'."""
    calendar = Calendar(workdays=calendar_workdays)
    rr = rruleset()
    rr.rrule(
        rrule(
            DAILY,
            byweekday=dateutil_workdays,
            dtstart=datetime.datetime(2010, 1, 1),
        )
    )
    for holiday in holidays:
        rr.exdate(holiday)
    dates = rr.between(
        datetime.datetime(2010, 1, 1),
        datetime.datetime(2013, 12, 31),
        inc=True,
    )
    return calendar, dates, holidays


test_data = {
    "western_week_no_holidays": create_calendar_test_data(
        None, (MO, TU, WE, TH, FR), []
    ),
    "western_week_with_holidays": create_calendar_test_data(
        None, (MO, TU, WE, TH, FR), _HOLIDAYS
    ),
    "middle_east_week_no_holidays": create_calendar_test_data(
        (0, 1, 2, 3, 6), (MO, TU, WE, TH, SU), []
    ),
    "middle_east_week_with_holidays": create_calendar_test_data(
        (0, 1, 2, 3, 6), (MO, TU, WE, TH, SU), _HOLIDAYS
    ),
    "monday_only_no_holidays": create_calendar_test_data(
        (0,), (MO,), []
    ),
    "monday_only_with_holidays": create_calendar_test_data(
        (0,), (MO,), _HOLIDAYS
    ),
}


@pytest.mark.parametrize(
    "calendar, dates, holidays", test_data.values(), ids=test_data.keys()
)
class TestCalendarMethods(object):
    def test_adjust_following(self, calendar, dates, holidays):
        """Tests adjusting a date forward."""
        i = -1
        date = dates[0]
        while date <= dates[-1]:
            dateadj = calendar.adjust(date, FOLLOWING)
            if date in dates:
                assert date == dateadj
                i += 1
            elif i < len(dates) - 1:
                assert dates[i + 1] == dateadj
            date += datetime.timedelta(days=1)

    def test_adjust_previous(self, calendar, dates, holidays):
        """Tests adjusting a date backwards."""
        i = -1
        date = dates[0]
        while date <= dates[-1]:
            dateadj = calendar.adjust(date, PREVIOUS)
            if date in dates:
                assert date == dateadj
                i += 1
            elif i >= 0:
                assert dateadj == dates
            date += datetime.timedelta(days=1)

    def test_adjust_modifiedfollowing(self, calendar, dates, holidays):
        """Tests adjusting a date forward with MODIFIED FOLLOWING."""
        i = -1
        date = dates[0]
        while date <= dates[-1]:
            dateadj = calendar.adjust(date, MODIFIEDFOLLOWING)
            if date in dates:
                assert date == dateadj
                i += 1
            elif 0 <= i < len(dates) - 1:
                j = i + (0 if dateadj.month != dates[i + 1].month else 1)
                assert dateadj == dates[j]
            date += datetime.timedelta(days=1)

    def test_isbusday(self, calendar, dates, holidays):
        """Tests that `isbuskday` returns `True` for known business days."""
        for i in range(len(dates)):
            date = dates[i]
            assert calendar.isbusday(date)
            if i > 0:
                d = (date - dates[i - 1]).days
                while d > 1:
                    date -= datetime.timedelta(days=1)
                    assert not calendar.isbusday(date)
                    d -= 1

    def test_isworkday(self, calendar, dates, holidays):
        """Tests that `isworkday` returns `True` for known work days."""
        for date in dates:
            assert calendar.isworkday(date)

    def test_isholiday(self, calendar, dates, holidays):
        """Tests that `isholiday` returns `True` for known holidays."""
        for date in holidays:
            assert not calendar.isworkday(date) and calendar.isholiday(date)

    def test_add_one_workday(self, calendar, dates, holidays):
        """Tests adding one work day."""
        for i in range(1, len(dates)):
            if holidays:
                calc_date = calendar.addbusdays(dates[i - 1], 1)
            else:
                calc_date = calendar.addworkdays(dates[i - 1], 1)
            assert calc_date == dates[i]

    def test_subtract_one_workday(self, calendar, dates, holidays):
        """Tests subtracting one work day."""
        for i in range(-2, -len(dates) - 1, -1):
            if holidays:
                calc_date = calendar.addbusdays(dates[i + 1], -1)
            else:
                calc_date = calendar.addworkdays(dates[i + 1], -1)
            assert calc_date == dates[i]

    def test_add_workdays(self, calendar, dates, holidays):
        """Tests adding multiple work days."""
        for i in range(0, len(dates)):
            if holidays:
                calc_date = calendar.addbusdays(dates[0], i)
            else:
                calc_date = calendar.addworkdays(dates[0], i)
            assert calc_date == dates[i]

    def test_subtract_workdays(self, calendar, dates, holidays):
        """Tests subtracting multiple work days."""
        for i in range(0, len(dates)):
            if holidays:
                calc_date = calendar.addbusdays(dates[-1], -i)
            else:
                calc_date = calendar.addworkdays(dates[-1], -i)
            assert calc_date == dates[-1 - i]

    def test_count_one_workday_forward(self, calendar, dates, holidays):
        """Tests counting one work day forward."""
        for i in range(1, len(dates)):
            if holidays:
                d = calendar.busdaycount(dates[i - 1], dates[i])
            else:
                d = calendar.workdaycount(dates[i - 1], dates[i])
            assert d == 1

    def test_count_one_workday_backward(self, calendar, dates, holidays):
        """Tests counting one work day backward."""
        for i in range(2, len(dates) + 1):
            if holidays:
                d = calendar.busdaycount(dates[-i], dates[-i + 1])
            else:
                d = calendar.workdaycount(dates[-i], dates[-i + 1])
            assert d == 1

    def test_count_workdays_forward(self, calendar, dates, holidays):
        """Tests counting multiple work days forward."""
        for i in range(0, len(dates)):
            if holidays:
                d = calendar.busdaycount(dates[0], dates[i])
            else:
                d = calendar.workdaycount(dates[0], dates[i])
            assert d == i

    def test_count_workdays_backward(self, calendar, dates, holidays):
        """Tests counting multiple work days backwards."""
        for i in range(0, len(dates)):
            if holidays:
                d = calendar.busdaycount(dates[-1], dates[-1 - i])
            else:
                d = calendar.workdaycount(dates[-1], dates[-1 - i])
            assert d == -i


#
# def test_add_one_workday_Jan01(self):
#     err_count = 0
#     for i in range(0, len(dates)):
#         if holidays:
#             calc_date = calendar.addbusdays("Jan 1, 2010", i + 1)
#         else:
#             calc_date = calendar.addbusdays("Jan 1, 2010", i)
#         if calc_date != dates[i]:
#             print(
#                 "Error [%s] got %s expected %s"
#                 % (dates[i - 1], calc_date, dates[i])
#             )
#             err_count += 1
#         if err_count > 10:
#             break
#     assert err_count == 0
#
#
#
#
# def test_eom(self):
#     print("test_eom")
#     err_count = 0
#     for i in range(1, len(dates)):
#         if dates[i].month != dates[i - 1].month:
#             date = dates[i - 1] - datetime.timedelta(days=10)
#             calc_date = calendar.buseom(date)
#             if dates[i - 1] != calc_date:
#                 print(
#                     "Error [%s-%s] got %s expected %s"
#                     % (
#                         dates[i - 1].year,
#                         dates[i - 1].month,
#                         calc_date,
#                         dates[i - 1],
#                     )
#                 )
#                 err_count += 1
#         if err_count > 10:
#             break
#     assert err_count == 0
#
#
# def test_range(self):
#     print("test_range")
#     cal_dates = list(calendar.range("2010-01-01", "Jan 1, 2014"))
#     assert cal_dates == dates
#     for i in range(0, 200, 5):
#         cal_dates = list(calendar.range(dates[i], dates[-i - 1]))
#         assert cal_dates == dates[i : -i - 1]
#     if not holidays:
#         return
#     for i in range(0, 20):
#         cal_dates = list(
#             calendar.range(holidays[i], holidays[-i - 1])
#         )
#         dates = self.rr.between(
#             holidays[i], holidays[-i - 1], inc=False
#         )
#         assert cal_dates == dates
#
#
# class TestCalendarWesternWeek(BaseCalendarTest):
#     @classmethod
#     def setup_class(cls):
#         print("\n\nTesting regular week, Mo-Fr, no holidays, 2010-2013")
#
#     def __init__(self):
#         BaseCalendarTest.__init__(self)
#         calendar = Calendar()
#         rr = rruleset()
#         rr.rrule(
#             rrule(
#                 DAILY,
#                 byweekday=(MO, TU, WE, TH, FR),
#                 dtstart=datetime.datetime(2010, 1, 1),
#             )
#         )
#         self.rr = rr
#         dates = rr.between(
#             datetime.datetime(2010, 1, 1),
#             datetime.datetime(2013, 12, 31),
#             inc=True,
#         )
#
#     def test_workdaycount_with_non_workday_dates(self):
#         print("test_workdaycount_with_non_workday_dates")
#         """ Jan 30th and 31st fall on a weekend """
#         daycount = 21
#         for date2 in ["Jan 30, 2010", "Jan 31, 2010", "Feb 1, 2010"]:
#             count = len(list(calendar.range("2010-01-01", date2)))
#             assert count == daycount
#         for date2 in ["Jan 29, 2010", "Jan 30, 2010", "Jan 31, 2010"]:
#             count = calendar.workdaycount("Dec 31, 2009", date2)
#             assert count == daycount
#
#
# class TestCalendarCrazyWeek(BaseCalendarTest):
#     @classmethod
#     def setup_class(cls):
#         print("\n\nTesting crazy week, Mo,Tu,Fr,Su, no holidays, 2010-2013")
#
#     def __init__(self):
#         BaseCalendarTest.__init__(self)
#         calendar = Calendar(workdays=[0, 1, 4, 6])
#         rr = rruleset()
#         rr.rrule(
#             rrule(
#                 DAILY,
#                 byweekday=(MO, TU, FR, SU),
#                 dtstart=datetime.datetime(2010, 1, 1),
#             )
#         )
#         self.rr = rr
#         dates = rr.between(
#             datetime.datetime(2010, 1, 1),
#             datetime.datetime(2013, 12, 31),
#             inc=True,
#         )
#
#
# class TestCalendarWesternWeekWithHolidays(BaseCalendarTest):
#     @classmethod
#     def setup_class(cls):
#         print("\n\nTesting regular week, Mo-Fr, WITH holidays, 2010-2013")
#         warnings.filterwarnings("ignore", module="business_calendar")
#
#     def __init__(self):
#         BaseCalendarTest.__init__(self)
#         holidays = [parse(x) for x in global_holidays.split("\n")]
#         calendar = Calendar(holidays=holidays)
#         calendar.warn_on_holiday_exhaustion = False
#         rr = rruleset()
#         rr.rrule(
#             rrule(
#                 DAILY,
#                 byweekday=(MO, TU, WE, TH, FR),
#                 dtstart=datetime.datetime(2010, 1, 1),
#             )
#         )
#         for h in holidays:
#             rr.exdate(h)
#         self.rr = rr
#         dates = rr.between(
#             datetime.datetime(2010, 1, 1),
#             datetime.datetime(2013, 12, 31),
#             inc=True,
#         )
#
#     def test_workdaycount_with_non_workday_dates(self):
#         print("test_workdaycount_with_non_workday_dates")
#         """ Jan 1st is a holiday, Jan 30th and 31st fall on a weekend """
#         daycount = 20
#         for date2 in ["Jan 30, 2010", "Jan 31, 2010", "Feb 1, 2010"]:
#             count = len(list(calendar.range("2010-01-01", date2)))
#             assert count == daycount
#         for date2 in ["Jan 29, 2010", "Jan 30, 2010", "Jan 31, 2010"]:
#             count = calendar.workdaycount("Dec 31, 2009", date2)
#             assert count == daycount + 1
#         for date2 in ["Jan 29, 2010", "Jan 30, 2010", "Jan 31, 2010"]:
#             count = calendar.busdaycount("Dec 31, 2009", date2)
#             assert count == daycount
#
#
# class TestCalendarCrazyWeekWithHolidays(BaseCalendarTest):
#     @classmethod
#     def setup_class(cls):
#         print("\n\nTesting crazy week, Mo,Tu,Fr,SU, WITH holidays, 2010-2013")
#         warnings.filterwarnings("ignore", module="business_calendar")
#
#     def __init__(self):
#         BaseCalendarTest.__init__(self)
#         holidays = [parse(x) for x in global_holidays.split("\n")]
#         calendar = Calendar(workdays=[0, 1, 4, 6], holidays=holidays)
#         rr = rruleset()
#         rr.rrule(
#             rrule(
#                 DAILY,
#                 byweekday=(MO, TU, FR, SU),
#                 dtstart=datetime.datetime(2010, 1, 1),
#             )
#         )
#         for h in holidays:
#             rr.exdate(h)
#         self.rr = rr
#         dates = rr.between(
#             datetime.datetime(2010, 1, 1),
#             datetime.datetime(2013, 12, 31),
#             inc=True,
#         )
#
#
# class TestCalendarCrazyWeek2WithHolidays(BaseCalendarTest):
#     @classmethod
#     def setup_class(cls):
#         print("\n\nTesting crazy week 2, Mo, WITH holidays, 2010-2013")
#         warnings.filterwarnings("ignore", module="business_calendar")
#
#     def __init__(self):
#         BaseCalendarTest.__init__(self)
#         holidays = [parse(x) for x in global_holidays.split("\n")]
#         calendar = Calendar(workdays=[0], holidays=holidays)
#         rr = rruleset()
#         rr.rrule(
#             rrule(DAILY, byweekday=(MO), dtstart=datetime.datetime(2010, 1, 1))
#         )
#         for h in holidays:
#             rr.exdate(h)
#         self.rr = rr
#         dates = rr.between(
#             datetime.datetime(2010, 1, 1),
#             datetime.datetime(2013, 12, 31),
#             inc=True,
#         )
