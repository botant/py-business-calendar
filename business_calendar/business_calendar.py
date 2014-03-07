"""
The business_calendar contains the main class Calendar.

This module doesn't require any third-party package but will use `dateutil`
for parsing if it is present. For testing however, `nose` and `dateutil`
are required.

In this module we adopt `weekdays()` notation, so Monday corresponds
to 0 and Sunday corresponds to 6, therefore there is a natural index of days
of the week as a list.

As default, `dateutil.parser.parse` is used as parser if dateutil is
found. Otherwise, a simple parser function expecting `%Y-%m-%d` is used.
You may **override** the parse function by assigning to the module variable
`parsefun`.

Classes:
    Calendar

Constants:
    MO, TU, WE, TH, FR, SA, SU,
    FOLLOWING, PREVIOUS, MODIFIEDFOLLOWING

Public Functions:
    parsefun

Warnings:
    CalendarHolidayWarning
"""
import bisect
import collections
import datetime
import warnings

__version__ = '0.1'
__all__ = ['Calendar',
           'FOLLOWING', 'PREVIOUS', 'MODIFIEDFOLLOWING',
           'MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU',
           'parsefun',
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
# pylint: disable=C0103
def _simpleparsefun(date):
    """Simple date parsing function"""
    if hasattr(date, 'year'):
        return date
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return date

def _dateutilparsefun(date):
    """dateutil parsing function"""
    if hasattr(date, 'year'):
        return date
    return _dateutil_parse(date)

try:
    from dateutil.parser import parse as _dateutil_parse
    parsefun = _dateutilparsefun
except ImportError:
    parsefun = _simpleparsefun


# warning function
class CalendarHolidayWarning(Warning):
    """Warning thrown by Calendar class"""
    pass

def warn(message):
    """Throw warning with a message"""
    warnings.warn(CalendarHolidayWarning(message), stacklevel=3)


# main class
# pylint: disable=R0912
class Calendar(object):
    """
    Class that represents a calendar with work and rest days, as well as
    holidays (which of course are rest days).

    Note:
        All functions will accept either a `str`, a `datetime.datetime` or a
        `datetime.date`, so this class is interactive enviroment-friendly.
        However, functions will return a proper datetime.datetime object
        whenever the argument is a str object.
    """

    # create internal index variables to speed up access to DayOfWeek
    # pylint: disable=W0142
    # pylint: disable=W0212
    # pylint: disable=E1101
    _idx_nextworkday = DayOfWeek._fields.index('nextworkday')
    _idx_offsetnext = DayOfWeek._fields.index('offsetnext')
    _idx_prevworkday = DayOfWeek._fields.index('prevworkday')
    _idx_offsetprev = DayOfWeek._fields.index('offsetprev')

    def __init__(self, workdays=None, holidays=None):
        """
        Initialize object and creates the week day map.

        Args:
            workdays: List or tuple of week days considered 'work days'.
                Anything not in this list is considered a rest day.
                Defaults to [MO, TU, WE, TH, FR].
            holidays: List or tuple of holidays (or strings).
                Default is [].
        """
        if workdays is None:
            self.workdays = [MO, TU, WE, TH, FR]
        else:
            self.workdays = sorted(list(set(workdays))) # sorted and unique

        if holidays is None:
            holidays = []

        # create week day map structure in local variable to speed up
        # this structure is the soul of this class, it is used in all
        # calculations and is the secret that enables the custom work day list
        weekdaymap = []
        for wkday in range(0, 7):
            wmap = {}
            wmap['dayofweek'] = wkday
            if wkday in self.workdays:
                wmap['isworkday'] = True
                i = self.workdays.index(wkday)
                # assign transition to next work day
                if i == len(self.workdays) - 1: # last work day of week
                    wmap['nextworkday'] = self.workdays[0]
                    wmap['offsetnext'] = wmap['nextworkday'] + 7 - wkday
                else:
                    wmap['nextworkday'] = self.workdays[i+1]
                    wmap['offsetnext'] = wmap['nextworkday'] - wkday
                # assign transition to previous work day
                if i == 0: # first work day of week
                    wmap['prevworkday'] = self.workdays[-1]
                    wmap['offsetprev'] = wmap['prevworkday'] - wkday - 7
                else:
                    wmap['prevworkday'] = self.workdays[i-1]
                    wmap['offsetprev'] = wmap['prevworkday'] - wkday
            else:
                wmap['isworkday'] = False
                # assign transition to next work day
                after = [x for x in range(wkday+1, 7) if x in self.workdays]
                if after: # there is a work day after this non-work day
                    wmap['nextworkday'] = after[0]
                    wmap['offsetnext'] = wmap['nextworkday'] - wkday
                else:
                    wmap['nextworkday'] = self.workdays[0]
                    wmap['offsetnext'] = wmap['nextworkday'] + 7 - wkday
                # assign transition to previous work day
                before = [x for x in range(0, wkday) if x in self.workdays]
                if before: # there is a work day before this non-work day
                    wmap['prevworkday'] = before[-1]
                    wmap['offsetprev'] = wmap['prevworkday'] - wkday
                else:
                    wmap['prevworkday'] = self.workdays[-1]
                    wmap['offsetprev'] = wmap['prevworkday'] - wkday - 7
            weekdaymap.append(DayOfWeek(**wmap))
        self.weekdaymap = weekdaymap

        # add holidays but eliminate non-work days and repetitions
        holidays = set([parsefun(hol) for hol in holidays])
        self.holidays = sorted(
            [hol for hol in holidays if weekdaymap[hol.weekday()].isworkday])

    def isworkday(self, date):
        """
        Check if a given date is a work date, ignoring holidays.

        Args:
            date (date, datetime or str): Date to be checked.

        Returns:
            bool: True if the date is a work date, False otherwise.
        """
        date = parsefun(date)
        return self.weekdaymap[date.weekday()].isworkday

    def isholiday(self, date):
        """
        Check if a given date is a holiday.

        Args:
            date (date, datetime or str): Date to be checked.

        Returns:
            bool: True if the date is a holiday, False otherwise.
        """
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
        """
        Check if a given date is a business date, taking into consideration
        the work days and holidays.

        Args:
            date (date, datetime or str): Date to be checked.

        Returns:
            bool: True if the date is a business date, False otherwise.
        """
        return self.isworkday(date) and not self.isholiday(date)

    def adjust(self, date, mode):
        """
        Adjust the date to the closest work date.

        Args:
            date (date, datetime or str): Date to be adjusted.
            mode (integer): FOLLOWING, PREVIOUS or MODIFIEDFOLLOWING.

        Note:
            If date is already a business date than it is returned unchanged.
            How to use the adjustment constants:

            **FOLLOWING**:
                Adjust to the next business date.
            **PREVIOUS**:
                Adjust to the previous business date.
            **MODIFIEDFOLLOWING**:
                Adjust to the next business date unless it falls on a
                different month, in which case adjust to the previous business
                date.

        Returns:
            datetime: Adjusted date.
        """
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
        """
        Add work days to a given date, ignoring holidays.

        Note:
            By definition, a zero offset causes the function to return the
            initial date, even it is not a work date. An offset of 1
            represents the next work date, regardless of date being a work
            date or not.

        Args:
            date (date, datetime or str): Date to be incremented.
            offset (integer): Number of work days to add. Positive values move
                the date forward and negative values move the date back.

        Returns:
            datetime: New incremented date.
        """
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
        """
        Add business days to a given date, taking holidays into consideration.

        Note:
            By definition, a zero offset causes the function to return the
            initial date, even it is not a business date. An offset of 1
            represents the next business date, regardless of date being a
            business date or not.

        Args:
            date (date, datetime or str): Date to be incremented.
            offset (integer): Number of business days to add. Positive values
                move the date forward and negative values move the date back.

        Returns:
            datetime: New incremented date.
        """
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
        """
        (PRIVATE) Count work days between two dates, ignoring holidays.
        """
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
        """
        Count work days between two dates, ignoring holidays.

        Args:
            date1 (date, datetime or str): Date start of interval.
            date2 (date, datetime or str): Date end of interval.

        Note:
            The adopted notation is COB to COB, so effectively date1 is not
            included in the calculation result.

        Example:
            >>> cal = Calendar()
            >>> date1 = datetime.datetime.today()
            >>> date2 = cal.addworkdays(date1, 1)
            >>> cal.workdaycount(date1, date2)
            1

        Returns:
            int: Number of work days between the two dates. If the dates
                are equal the result is zero. If date1 > date2 the result is
                negative.
        """
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
        """
        Count business days between two dates (private), taking holidays into
        consideration.

        Args:
            date1 (date, datetime or str): Date start of interval.
            date2 (date, datetime or str): Date end of interval.

        Note:
            The adopted notation is COB to COB, so effectively date1 is not
            included in the calculation result.

        Example:
            >>> cal = Calendar()
            >>> date1 = datetime.datetime.today()
            >>> date2 = cal.addbusdays(date1, 1)
            >>> cal.busdaycount(date1, date2)
            1

        Returns:
            int: Number of business days between the two dates. If the dates
                are equal the result is zero. If date1 > date2 the result is
                negative.
        """
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

    @staticmethod
    def caleom(date):
        """
        Adjust date to last day of the month, regardless of work days.

        Args:
            date (date, datetime or str): Date to be adjusted.

        Returns:
            datetime: Adjusted date.
        """
        date = parsefun(date)
        date += datetime.timedelta(days=32-date.day)
        date -= datetime.timedelta(days=date.day)
        return date

    def buseom(self, date):
        """
        Adjust date to last business day of the month, taking holidays into
        consideration.

        Args:
            date (date, datetime or str): Date to be adjusted.

        Returns:
            datetime: Adjusted date.
        """
        return self.adjust(self.caleom(date), PREVIOUS)

    def range(self, date1, date2):
        """
        Generate business days between two dates, taking holidays into
        consideration.

        Args:
            date1 (date, datetime or str): Date start of interval.
            date2 (date, datetime or str): Date end of interval, not included.

        Note:
            All business days between date1 (inc) and date2 (exc) are returned,
            and date2 must be bigger than date1.

        Yields:
            datetime: Business days in the specified range.
        """
        date1 = self.adjust(parsefun(date1), FOLLOWING)
        date2 = parsefun(date2)

        holidays = []
        holidx = 0
        if len(self.holidays):
            index1 = bisect.bisect_left(self.holidays, date1)
            index2 = bisect.bisect_left(self.holidays, date2)
            if index2 > index1:
                holidays = self.holidays[index1:index2]

        datewk = date1.weekday()
        while date1 < date2:
            if (holidx < len(holidays)) and (holidays[holidx] == date1):
                holidx += 1
            else:
                yield date1
            date1 += datetime.timedelta(days=\
                                        self.weekdaymap[datewk].offsetnext)
            datewk = self.weekdaymap[datewk].nextworkday

