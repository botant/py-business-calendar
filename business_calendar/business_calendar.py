"""
business_calendar

A simple class that handles business day calculations, including custom work
days and holidays.

This class is interactive environment friendly, so all functions that expect
datetime arguments will also accept strings.

Doesn't require any third-party package, except dateutil, which will be used
for parsing if it is present. For testing however, nose and dateutil are
required.

NOTES:
1) In this package we adopt weekdays, so Monday corresponds to 0 and
   Sunday corresponds to 6, therefore there is a natural index of days of the
   week as a list.
2) As default, dateutil.parser.parse is used as parser if dateutil is found.
   Otherwise, a simple parser function expecting %Y-%m-%d is used. You may
   override the parse function by assigning to the module variable 'parsefun'.
"""
import bisect
import collections
import datetime
import warnings

__version__ = '0.1'
__all__ = ['Calendar', 'FOLLOWING', 'PREVIOUS', 'MODIFIEDFOLLOWING',
           'MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU',
           'parsefun', 'warn',
           'CalendarHolidayWarning']

# constants used in date functions
FOLLOWING = 1
PREVIOUS = 2
MODIFIEDFOLLOWING = 3

MO = 0
TU = 1
WE = 2
TH = 3
FR = 4
SA = 5
SU = 6

# named tuple used in Calendar class
DayOfWeek = collections.namedtuple('DayOfWeek', ['dayofweek', 'isworkday',
                                                 'nextworkday', 'offsetnext',
                                                 'prevworkday', 'offsetprev'])

# portable function to parse dates
def _simpleparsefun(date):
    if hasattr(date, 'year'):
        return date
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except:
        date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return date

def _dateutilparsefun(date):
    if hasattr(date, 'year'):
        return date
    return _dateutil_parse(date)

try:
    from dateutil.parser import parse as _dateutil_parse
    parsefun = _dateutilparsefun
except:
    parsefun = _simpleparsefun

# warning function
class CalendarHolidayWarning(Warning): pass

def warn(message):
    warnings.warn(CalendarHolidayWarning(message), stacklevel=3)

# main class
class Calendar(object):

    _idx_nextworkday = DayOfWeek._fields.index('nextworkday')
    _idx_offsetnext = DayOfWeek._fields.index('offsetnext')
    _idx_prevworkday = DayOfWeek._fields.index('prevworkday')
    _idx_offsetprev = DayOfWeek._fields.index('offsetprev')

    def __init__(self, workdays=[MO,TU,WE,TH,FR], holidays=[]):
        self.workdays = sorted(list(set(workdays))) # sorted and unique

        # create week day map structure in local variable to speed up function
        weekdaymap = []
        for wk in range(0,7):
            wmap = {}
            wmap['dayofweek'] = wk
            if wk in self.workdays:
                wmap['isworkday'] = True
                i = self.workdays.index(wk)
                # assign transition to next work day
                if i == len(self.workdays) - 1: # last work day of week
                    wmap['nextworkday'] = self.workdays[0]
                    wmap['offsetnext'] = wmap['nextworkday'] + 7 - wk
                else:
                    wmap['nextworkday'] = self.workdays[i+1]
                    wmap['offsetnext'] = wmap['nextworkday'] - wk
                # assign transition to previous work day
                if i == 0: # first work day of week
                    wmap['prevworkday'] = self.workdays[-1]
                    wmap['offsetprev'] = wmap['prevworkday'] - wk - 7
                else:
                    wmap['prevworkday'] = self.workdays[i-1]
                    wmap['offsetprev'] = wmap['prevworkday'] - wk
            else:
                wmap['isworkday'] = False
                # assign transition to next work day
                after = [x for x in range(wk+1,7) if x in self.workdays]
                if after: # there is a work day after this non-work day
                    wmap['nextworkday'] = after[0]
                    wmap['offsetnext'] = wmap['nextworkday'] - wk
                else:
                    wmap['nextworkday'] = self.workdays[0]
                    wmap['offsetnext'] = wmap['nextworkday'] + 7 - wk
                # assign transition to previous work day
                before = [x for x in range(0,wk) if x in self.workdays]
                if before: # there is a work day before this non-work day
                    wmap['prevworkday'] = before[-1]
                    wmap['offsetprev'] = wmap['prevworkday'] - wk
                else:
                    wmap['prevworkday'] = self.workdays[-1]
                    wmap['offsetprev'] = wmap['prevworkday'] - wk - 7
            weekdaymap.append(DayOfWeek(**wmap))
        self.weekdaymap = weekdaymap

        # add holidays but eliminate non-work days and repetitions
        holidays = set([parsefun(h) for h in holidays])
        self.holidays = sorted(
            [h for h in holidays if weekdaymap[h.weekday()].isworkday])

    def isworkday(self, date):
        date = parsefun(date)
        return self.weekdaymap[date.weekday()].isworkday

    def isholiday(self, date):
        date = parsefun(date)
        if self.holidays:
            # i is the index of first holiday >= date
            i = bisect.bisect_left(self.holidays, date)
            if i == 0 and date < self.holidays[0]:
                warn('Holiday list exhausted at start, ' \
                     'isholiday(%s) output may be incorrect.' % date)
            elif i == len(self.holidays):
                warn('Holiday list exhausted at end, ' \
                     'isholiday(%s) output may be incorrect.' % date)
            elif self.holidays[i] == date:
                return True
        return False

    def isbusday(self, date):
        return self.isworkday(date) and not self.isholiday(date)

    def adjust(self, date, mode):
        date = parsefun(date)
        if self.isbusday(date):
            return date

        if mode == FOLLOWING:
            dateadj = self.addbusdays(date, 1)
        elif mode == PREVIOUS:
            dateadj = self.addbusdays(date, -1)
        elif mode == MODIFIEDFOLLOWING:
            dateadj = self.addbusdays(date, 1)
            if dateadj.month != date.month:
                dateadj = self.addbusdays(dateadj, -1)
        else:
            raise ValueError('Invalid mode %s' % mode)

        return dateadj

    def addworkdays(self, date, offset):
        date = parsefun(date)
        if offset == 0:
            return date

        if offset > 0:
            direction = 1
            idx_offset = Calendar._idx_offsetnext
            idx_next = Calendar._idx_nextworkday
            idx_offset_other = Calendar._idx_offsetprev
            idx_next_other = Calendar._idx_prevworkday
        else:
            direction = -1
            idx_offset = Calendar._idx_offsetprev
            idx_next = Calendar._idx_prevworkday
            idx_offset_other = Calendar._idx_offsetnext
            idx_next_other = Calendar._idx_nextworkday

        # adjust date to first work day before/after so counting always
        # starts from a workday
        weekdaymap = self.weekdaymap # speed up
        datewk = date.weekday()
        if not weekdaymap[datewk].isworkday:
            date += datetime.timedelta(days=\
                                        weekdaymap[datewk][idx_offset_other])
            datewk = weekdaymap[datewk][idx_next_other]

        nw, nd = divmod(abs(offset), len(self.workdays))
        ndays = nw * 7
        while nd > 0:
            ndays += abs(weekdaymap[datewk][idx_offset])
            datewk = weekdaymap[datewk][idx_next]
            nd -= 1

        date += datetime.timedelta(days=ndays*direction)
        return date

    def addbusdays(self, date, offset):
        date = parsefun(date)
        if offset == 0:
            return date

        dateoffset = self.addworkdays(date, offset)
        holidays = self.holidays # speed up
        if not holidays:
            return dateoffset

        weekdaymap = self.weekdaymap # speed up
        datewk = dateoffset.weekday()
        if offset > 0:
            # i is the index of first holiday > date
            # we don't care if the start date is a holiday
            i = bisect.bisect_right(holidays, date)
            if i == len(holidays):
                warn('Holiday list exhausted at end, ' \
                     'addbusday(%s,%s) output may be incorrect.' % \
                     (date, offset))
            else:
                while holidays[i] <= dateoffset:
                    dateoffset += datetime.timedelta(days=\
                                                weekdaymap[datewk].offsetnext)
                    datewk = weekdaymap[datewk].nextworkday
                    i += 1
                    if i == len(holidays):
                        warn('Holiday list exhausted at end, ' \
                             'addbusday(%s,%s) output may be incorrect.' % \
                             (date, offset))
                        break
        else:
            # i is the index of first holiday >= date
            # we don't care if the start date is a holiday
            i = bisect.bisect_left(holidays, date) - 1
            if i == -1:
                warn('Holiday list exhausted at start, ' \
                     'addbusday(%s,%s) output may be incorrect.' \
                     % (date, offset))
            else:
                while holidays[i] >= dateoffset:
                    dateoffset += datetime.timedelta(days=\
                                                weekdaymap[datewk].offsetprev)
                    datewk = weekdaymap[datewk].prevworkday
                    i -= 1
                    if i == -1:
                        warn('Holiday list exhausted at start, ' \
                             'addbusday(%s,%s) output may be incorrect.' % \
                             (date, offset))
                        break

        return dateoffset

    def _workdaycount(self, date1, date2):
        nw, nd = divmod((date2 - date1).days, 7)
        ndays = nw * len(self.workdays)
        if nd > 0:
            date1wd = date1.weekday()
            date2wd = date2.weekday()
            while date1wd != date2wd:
                ndays += 1
                date1wd = self.weekdaymap[date1wd].nextworkday
        return ndays

    def workdaycount(self, date1, date2):
        date1 = parsefun(date1)
        date2 = parsefun(date2)
        if date1 == date2:
            return 0
        elif date1 > date2:
            date1, date2 = date2, date1
            direction = -1
        else:
            direction = 1

        ndays = self._workdaycount(date1, date2)
        return ndays * direction

    def busdaycount(self, date1, date2):
        date1 = parsefun(date1)
        date2 = parsefun(date2)
        if date1 == date2:
            return 0
        elif date1 > date2:
            date1, date2 = date2, date1
            direction = -1
        else:
            direction = 1

        ndays = self._workdaycount(date1, date2)

        if self.holidays:
            holidays = self.holidays # speed up
            if date1 > holidays[-1]:
                warn('Holiday list exhausted at end, ' \
                     'busdaycount(%s,%s) output may be incorrect.' % \
                     (date1, date2))
            elif date2 < holidays[0]:
                warn('Holiday list exhausted at start, ' \
                     'busdaycount(%s,%s) output may be incorrect.' % \
                     (date1, date2))
            else:
                if date1 < holidays[0]:
                    warn('Holiday list exhausted at start, ' \
                         'busdaycount(%s,%s) output may be incorrect.' % \
                         (date1, date2))
                if date2 > holidays[-1]:
                    warn('Holiday list exhausted at end, ' \
                         'busdaycount(%s,%s) output may be incorrect.' % \
                         (date1, date2))
                # i is the index of first holiday > date
                # we don't care if the start date is a holiday
                i = bisect.bisect_right(holidays, date1)
                while holidays[i] <= date2:
                    ndays -= 1
                    i += 1
                    if i == len(holidays):
                        break

        return ndays * direction

    def caleom(self, date):
        date = parsefun(date)
        date += datetime.timedelta(days=32-date.day)
        date -= datetime.timedelta(days=date.day)
        return date

    def buseom(self, date):
        return self.adjust(self.caleom(date), PREVIOUS)

    def range(self, date1, date2):
        date1 = self.adjust(parsefun(date1), FOLLOWING)
        date2 = parsefun(date2)

        holidays = []
        holidx = 0
        if len(self.holidays):
            ia = bisect.bisect_left(self.holidays, date1)
            ib = bisect.bisect_left(self.holidays, date2)
            if ib > ia:
                holidays = self.holidays[ia:ib]

        datewk = date1.weekday()
        while date1 < date2:
            if (holidx < len(holidays)) and (holidays[holidx] == date1):
                holidx += 1
            else:
                yield date1
            date1 += datetime.timedelta(days=\
                                        self.weekdaymap[datewk].offsetnext)
            datewk = self.weekdaymap[datewk].nextworkday

