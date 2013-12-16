import datetime
import warnings
from business_calendar import Calendar, FOLLOWING, PREVIOUS, MODIFIEDFOLLOWING
from dateutil.rrule import rruleset, rrule, DAILY, MO, TU, WE, TH, FR, SA, SU
from dateutil.parser import parse


global_holidays = \
"""
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
"""

class BaseCalendarTest(object):
    def __init__(self):
        self.cal = None
        self.dates = None
        self.holidays = []

    def setup(self):
        print('')

    def test_adjust_following(self):
        print('test_adjust_following')
        err_count = 0
        i = -1
        date = self.dates[0]
        while date <= self.dates[-1]:
            dateadj = self.cal.adjust(date, FOLLOWING)
            if date in self.dates:
                i += 1
                if date != dateadj:
                    print('Error [%s] adjusted to %s, expected same' % \
                        (date, dateadj))
                    err_count += 1
            elif i < len(self.dates)-1:
                if dateadj != self.dates[i+1]:
                    print('Error [%s] adjusted to %s, expected %s' % \
                        (date, dateadj, self.dates[i+1]))
                    err_count += 1
            if err_count > 10:
                break
            date += datetime.timedelta(days=1)
        assert err_count == 0

    def test_adjust_previous(self):
        print('test_adjust_previous')
        err_count = 0
        i = -1
        date = self.dates[0]
        while date <= self.dates[-1]:
            dateadj = self.cal.adjust(date, PREVIOUS)
            if date in self.dates:
                i += 1
                if date != dateadj:
                    print('Error [%s] adjusted to %s, expected same' % \
                        (date, dateadj))
                    err_count += 1
            elif i >= 0:
                if dateadj != self.dates[i]:
                    print('Error [%s] adjusted to %s, expected %s' % \
                        (date, dateadj, self.dates[i]))
                    err_count += 1
            if err_count > 10:
                break
            date += datetime.timedelta(days=1)
        assert err_count == 0

    def test_adjust_modifiedfollowing(self):
        print('test_adjust_modifiedfollowing')
        err_count = 0
        i = -1
        date = self.dates[0]
        while date <= self.dates[-1]:
            dateadj = self.cal.adjust(date, MODIFIEDFOLLOWING)
            if date in self.dates:
                i += 1
                if date != dateadj:
                    print('Error [%s] adjusted to %s, expected same' % \
                        (date, dateadj))
                    err_count += 1
            elif i >= 0 and i < len(self.dates)-1:
                j = i + (0 if dateadj.month != self.dates[i+1].month else 1)
                if dateadj != self.dates[j]:
                    print('Error [%s] adjusted to %s, expected %s' % \
                        (date, dateadj, self.dates[j]))
                    err_count += 1
            if err_count > 10:
                break
            date += datetime.timedelta(days=1)
        assert err_count == 0

    def test_isbusday(self):
        print('test_isbusday')
        err_count = 0
        for i in range(len(self.dates)):
            date = self.dates[i]
            if not self.cal.isbusday(date):
                print('Error [%s] should be a business day' % date)
                err_count += 1
            if i > 0:
                d = (date - self.dates[i-1]).days
                while d > 1:
                    date -= datetime.timedelta(days=1)
                    if self.cal.isbusday(date):
                        print('Error [%s] should NOT be a business day' % date)
                        err_count += 1
                    d -= 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_isworkday(self):
        print('test_isworkday')
        err_count = 0
        for date in self.dates:
            if not self.cal.isworkday(date):
                print('Error [%s] should be a work day' % date)
                err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_isholiday(self):
        print('test_isholiday')
        err_count = 0
        for date in self.holidays:
            if self.cal.isworkday(date) and not self.cal.isholiday(date):
                print('Error [%s] should be a holiday' % date)
                err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_add_one_workday(self):
        print('test_add_one_workday')
        err_count = 0
        for i in range(1, len(self.dates)):
            if self.holidays:
                calc_date = self.cal.addbusdays(self.dates[i-1], 1)
            else:
                calc_date = self.cal.addworkdays(self.dates[i-1], 1)
            if calc_date != self.dates[i]:
                print('Error [%s] got %s expected %s' % (self.dates[i-1],
                                                         calc_date,
                                                         self.dates[i]))
                err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_add_one_workday__Jan01(self):
        print('test_add_one_workday__Jan01')
        err_count = 0
        for i in range(0, len(self.dates)):
            if self.holidays:
                calc_date = self.cal.addbusdays('Jan 1, 2010', i+1)
            else:
                calc_date = self.cal.addbusdays('Jan 1, 2010', i)
            if calc_date != self.dates[i]:
                print('Error [%s] got %s expected %s' % (self.dates[i-1],
                                                         calc_date,
                                                         self.dates[i]))
                err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_subtract_one_workday(self):
        print('test_subtract_one_workday')
        err_count = 0
        for i in range(-2, -len(self.dates)-1, -1):
            if self.holidays:
                calc_date = self.cal.addbusdays(self.dates[i+1], -1)
            else:
                calc_date = self.cal.addworkdays(self.dates[i+1], -1)
            if calc_date != self.dates[i]:
                print('Error [%s] got %s expected %s' % (self.dates[i+1],
                                                         calc_date,
                                                         self.dates[i]))
                err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_add_workdays(self):
        print('test_add_workdays')
        err_count = 0
        for i in range(0, len(self.dates)):
            if self.holidays:
                calc_date = self.cal.addbusdays(self.dates[0], i)
            else:
                calc_date = self.cal.addworkdays(self.dates[0], i)
            if calc_date != self.dates[i]:
                print('Error [%s] got %s expected %s' % (i, calc_date,
                                                         self.dates[i]))
                err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_subtract_workdays(self):
        print('test_subtract_workdays')
        err_count = 0
        for i in range(0, len(self.dates)):
            if self.holidays:
                calc_date = self.cal.addbusdays(self.dates[-1], -i)
            else:
                calc_date = self.cal.addworkdays(self.dates[-1], -i)
            if calc_date != self.dates[-1-i]:
                print('Error [%s] got %s expected %s' % (-i, calc_date,
                                                         self.dates[-1-i]))
                err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_count_one_workday_forward(self):
        print('test_count_one_workday_forward')
        err_count = 0
        for i in range(1, len(self.dates)):
            if self.holidays:
                d = self.cal.busdaycount(self.dates[i-1], self.dates[i])
            else:
                d = self.cal.workdaycount(self.dates[i-1], self.dates[i])
            if d != 1:
                print('Error [%s-%s] got %s expected 1' % (self.dates[i-1],
                                                           self.dates[i], d))
                err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_count_one_workday_backward(self):
        print('test_count_one_workday_backward')
        err_count = 0
        for i in range(2, len(self.dates)+1):
            if self.holidays:
                d = self.cal.busdaycount(self.dates[-i], self.dates[-i+1])
            else:
                d = self.cal.workdaycount(self.dates[-i], self.dates[-i+1])
            if d != 1:
                print('Error [%s-%s] got %s expected 1' % (self.dates[-i],
                                                           self.dates[-i+1],
                                                           d))
                err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_count_workdays_forward(self):
        print('test_count_workday_forward')
        err_count = 0
        for i in range(0, len(self.dates)):
            if self.holidays:
                d = self.cal.busdaycount(self.dates[0], self.dates[i])
            else:
                d = self.cal.workdaycount(self.dates[0], self.dates[i])
            if d != i:
                print('Error [%s-%s] got %s expected %s' % (self.dates[0],
                                                            self.dates[i],
                                                            d, i))
                err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_count_workdays_backward(self):
        print('test_count_workday_backward')
        err_count = 0
        for i in range(0, len(self.dates)):
            if self.holidays:
                d = self.cal.busdaycount(self.dates[-1], self.dates[-1-i])
            else:
                d = self.cal.workdaycount(self.dates[-1], self.dates[-1-i])
            if d != -i:
                print('Error [%s-%s] got %s expected %s' % (self.dates[-1],
                                                            self.dates[-1-i],
                                                            d, -i))
                err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_eom(self):
        print('test_eom')
        err_count = 0
        for i in range(1, len(self.dates)):
            if self.dates[i].month != self.dates[i-1].month:
                date = self.dates[i-1] - datetime.timedelta(days=10)
                calc_date = self.cal.buseom(date)
                if self.dates[i-1] != calc_date:
                    print('Error [%s-%s] got %s expected %s' % \
                        (self.dates[i-1].year, self.dates[i-1].month,
                         calc_date, self.dates[i-1]))
                    err_count += 1
            if err_count > 10:
                break
        assert err_count == 0

    def test_range(self):
        print('test_range')
        cal_dates = list(self.cal.range('2010-01-01', 'Jan 1, 2014'))
        assert cal_dates == self.dates
        for i in range(0, 200, 5):
            cal_dates = list(self.cal.range(self.dates[i], self.dates[-i-1]))
            assert cal_dates == self.dates[i:-i-1]
        if not self.holidays:
            return
        for i in range(0, 20):
            cal_dates = list(self.cal.range(self.holidays[i],
                                            self.holidays[-i-1]))
            dates = self.rr.between(self.holidays[i], self.holidays[-i-1],
                                    inc=False)
            assert cal_dates == dates


class TestCalendarWesternWeek(BaseCalendarTest):
    @classmethod
    def setup_class(cls):
        print('\n\nTesting regular week, Mo-Fr, no holidays, 2010-2013')

    def __init__(self):
        BaseCalendarTest.__init__(self)
        self.cal = Calendar()
        rr = rruleset()
        rr.rrule(rrule(DAILY,
                       byweekday=(MO,TU,WE,TH,FR),
                       dtstart=datetime.datetime(2010,1,1)))
        self.rr = rr
        self.dates = rr.between(datetime.datetime(2010,1,1),
                                datetime.datetime(2013,12,31),
                                inc=True)

class TestCalendarCrazyWeek(BaseCalendarTest):
    @classmethod
    def setup_class(cls):
        print('\n\nTesting crazy week, Mo,Tu,Fr,Su, no holidays, 2010-2013')

    def __init__(self):
        BaseCalendarTest.__init__(self)
        self.cal = Calendar(workdays=[0,1,4,6])
        rr = rruleset()
        rr.rrule(rrule(DAILY,
                       byweekday=(MO,TU,FR,SU),
                       dtstart=datetime.datetime(2010,1,1)))
        self.rr = rr
        self.dates = rr.between(datetime.datetime(2010,1,1),
                                datetime.datetime(2013,12,31),
                                inc=True)

class TestCalendarWesternWeekWithHolidays(BaseCalendarTest):
    @classmethod
    def setup_class(cls):
        print('\n\nTesting regular week, Mo-Fr, WITH holidays, 2010-2013')
        warnings.filterwarnings('ignore', module='business_calendar')

    def __init__(self):
        BaseCalendarTest.__init__(self)
        self.holidays = [parse(x) for x in global_holidays.split('\n')]
        self.cal = Calendar(holidays=self.holidays)
        self.cal.warn_on_holiday_exhaustion = False
        rr = rruleset()
        rr.rrule(rrule(DAILY,
                       byweekday=(MO,TU,WE,TH,FR),
                       dtstart=datetime.datetime(2010,1,1)))
        for h in self.holidays:
            rr.exdate(h)
        self.rr = rr
        self.dates = rr.between(datetime.datetime(2010,1,1),
                                datetime.datetime(2013,12,31),
                                inc=True)

class TestCalendarCrazyWeekWithHolidays(BaseCalendarTest):
    @classmethod
    def setup_class(cls):
        print('\n\nTesting crazy week, Mo,Tu,Fr,SU, WITH holidays, 2010-2013')
        warnings.filterwarnings('ignore', module='business_calendar')

    def __init__(self):
        BaseCalendarTest.__init__(self)
        self.holidays = [parse(x) for x in global_holidays.split('\n')]
        self.cal = Calendar(workdays=[0,1,4,6], holidays=self.holidays)
        rr = rruleset()
        rr.rrule(rrule(DAILY,
                       byweekday=(MO,TU,FR,SU),
                       dtstart=datetime.datetime(2010,1,1)))
        for h in self.holidays:
            rr.exdate(h)
        self.rr = rr
        self.dates = rr.between(datetime.datetime(2010,1,1),
                                datetime.datetime(2013,12,31),
                                inc=True)

class TestCalendarCrazyWeek2WithHolidays(BaseCalendarTest):
    @classmethod
    def setup_class(cls):
        print('\n\nTesting crazy week 2, Mo, WITH holidays, 2010-2013')
        warnings.filterwarnings('ignore', module='business_calendar')

    def __init__(self):
        BaseCalendarTest.__init__(self)
        self.holidays = [parse(x) for x in global_holidays.split('\n')]
        self.cal = Calendar(workdays=[0], holidays=self.holidays)
        rr = rruleset()
        rr.rrule(rrule(DAILY,
                       byweekday=(MO),
                       dtstart=datetime.datetime(2010,1,1)))
        for h in self.holidays:
            rr.exdate(h)
        self.rr = rr
        self.dates = rr.between(datetime.datetime(2010,1,1),
                                datetime.datetime(2013,12,31),
                                inc=True)