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
    calendar = Calendar(workdays=calendar_workdays, holidays=holidays)
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
    "monday_only_no_holidays": create_calendar_test_data((0,), (MO,), []),
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
            else:
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
            else:
                assert dateadj == dates[i]
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
            else:
                j = i + (0 if dateadj.month != dates[i + 1].month else 1)
                assert dateadj == dates[j]
            date += datetime.timedelta(days=1)

    def test_isbusday(self, calendar, dates, holidays):
        """Tests that `isbusday` returns `True` for known business days."""
        for i in range(len(dates)):
            date = dates[i]
            assert calendar.isbusday(date)
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
            assert calendar.isholiday(date) or not calendar.isworkday(date)

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

    def test_eom(self, calendar, dates, holidays):
        """Tests End of Month calculation."""
        for i in range(1, len(dates)):
            if dates[i].month != dates[i - 1].month:
                date = dates[i - 1] - datetime.timedelta(days=10)
                calc_date = calendar.buseom(date)
                assert dates[i - 1] == calc_date

    def test_range(self, calendar, dates, holidays):
        """Tests date range."""
        cal_dates = list(calendar.range("2010-01-01", "Jan 1, 2014"))
        assert cal_dates == dates
        for i in range(0, 200, 5):
            cal_dates = list(calendar.range(dates[i], dates[-i - 1]))
            assert cal_dates == dates[i : -i - 1]


@pytest.mark.parametrize(
    "calendar, dates, holidays",
    [
        test_data["western_week_no_holidays"],
        test_data["western_week_with_holidays"],
    ],
    ids=["western_week_no_holidays", "western_week_with_holidays"],
)
def test_workdaycount_on_non_work_day(calendar, dates, holidays):
    """Tests workday count on non workday."""
    # Jan 30th and 31st fall on a weekend.
    # Jan 1st may or may not be a holiday.
    if datetime.datetime(2010, 1, 1) in holidays:
        daycount_jan_1st = 20
        daycount_dec_31st = 21
    else:
        daycount_jan_1st = 21
        daycount_dec_31st = 21

    for date2 in ["Jan 30, 2010", "Jan 31, 2010", "Feb 1, 2010"]:
        count = len(list(calendar.range("2010-01-01", date2)))
        assert count == daycount_jan_1st
    for date2 in ["Jan 29, 2010", "Jan 30, 2010", "Jan 31, 2010"]:
        count = calendar.workdaycount("Dec 31, 2009", date2)
        assert count == daycount_dec_31st


def test_busdaycount_holiday_boundaries():
    """Tests busdaycount when the boundaries are holidays."""
    # 2017-07-04 is a Tuesday.
    calendar = Calendar(holidays=["2017-07-04"])
    count = calendar.busdaycount("2017-07-04", "2017-07-05")
    assert count == 1
    count = calendar.busdaycount("2017-07-03", "2017-07-04")
    assert count == 0
