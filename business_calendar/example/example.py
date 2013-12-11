from business_calendar import Calendar, MO, TU, WE, TH, FR
import datetime
date1 = datetime.datetime(2013,1,10)

# normal calendar, no holidays
cal = Calendar()
date2 = cal.addbusdays(date1, 25)
print('%s days between %s and %s' % \
    (cal.busdaycount(date1, date2), date1, date2))

# don't work on Fridays? no problem!
cal = Calendar(workdays=[MO,TU,WE,TH])
date2 = cal.addbusdays(date1, 25)
print('%s days between %s and %s' % \
    (cal.busdaycount(date1, date2), date1, date2))

# holiday? no problem!
cal = Calendar(workdays=[MO,TU,WE,TH], holidays=['2013-01-17'])
date2 = cal.addbusdays(date1, 25)
print('%s days between %s and %s' % \
    (cal.busdaycount(date1, date2), date1, date2))
