from business_calendar import Calendar
from dateutil.rrule import rruleset, rrule, DAILY, MO, TU, WE, TH, FR
from dateutil.parser import parse
import datetime

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

holidays = [parse(x) for x in global_holidays.split('\n')]

def init_calendar():
    return Calendar(holidays=holidays)

def init_rruleset():
    rr = rruleset()
    rr.rrule(rrule(DAILY,
                   byweekday=(MO,TU,WE,TH,FR),
                   dtstart=datetime.datetime(2010,1,1)))
    for h in holidays:
        rr.exdate(h)
    return rr


cal = init_calendar()
rr = init_rruleset()

def gen_calendar_1():
    cal.range(datetime.datetime(2010,1,1), datetime.datetime(2013,12,31))

def gen_rruleset_1():
    rr.between(datetime.datetime(2010,1,1), datetime.datetime(2013,12,31),
               inc=True)

def gen_calendar_2():
    cal.range(datetime.datetime(2010,1,1), datetime.datetime(2010,3,1))

def gen_rruleset_2():
    rr.between(datetime.datetime(2010,1,1), datetime.datetime(2010,3,1),
               inc=True)

def gen_calendar_3():
    cal.range(datetime.datetime(1970,1,1), datetime.datetime(2030,12,31))

def gen_rruleset_3():
    rr.between(datetime.datetime(1970,1,1), datetime.datetime(2030,12,31),
               inc=True)

import timeit

t = timeit.repeat('init_calendar', repeat=3, number=10000000,
                  setup='from __main__ import init_calendar')
print('init cal: %.6fs' % min(t))

t = timeit.repeat('init_rruleset', repeat=3, number=10000000,
                  setup='from __main__ import init_rruleset')
print('init rr: %.6fs' % min(t))

t = timeit.repeat('gen_calendar_1', repeat=3, number=10000000,
                  setup='from __main__ import gen_calendar_1')
print('gen cal medium: %.6fs' % min(t))

t = timeit.repeat('gen_rruleset_1', repeat=3, number=10000000,
                  setup='from __main__ import gen_rruleset_1')
print('gen rr medium: %.6fs' % min(t))

t = timeit.repeat('gen_calendar_2', repeat=3, number=10000000,
                  setup='from __main__ import gen_calendar_2')
print('gen cal short: %.6fs' % min(t))

t = timeit.repeat('gen_rruleset_2', repeat=3, number=10000000,
                  setup='from __main__ import gen_rruleset_2')
print('gen rr short: %.6fs' % min(t))

t = timeit.repeat('gen_calendar_3', repeat=3, number=10000000,
                  setup='from __main__ import gen_calendar_3')
print('gen cal long: %.6fs' % min(t))

t = timeit.repeat('gen_rruleset_3', repeat=3, number=10000000,
                  setup='from __main__ import gen_rruleset_3')
print('gen rr long: %.6fs' % min(t))
