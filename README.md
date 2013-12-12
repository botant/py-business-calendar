# business_calendar #

**business_calendar** is a Python package that implements simple business days calculations. You can use a custom work week and a holiday list.

## Motivation ##

Python has many different implementations of datetime functions in `datetime`, `dateutil`, `numpy` and `pandas`. However, none of these is complete and implements all set of business days functionality needed for real-life applications.


- `datetime`: basic date framework without any business day functionality at all.
- `dateutil`: fantastic package with lots of cool features, but it is built around `rrule` and `rruleset` which are date generators, therefore not very easy to use in simple calculations.
- `numpy`: datetime functions were added in version 1.7.0, and although promissing, they suffer from a few problems:
  - all calculations are performed on `np.datetime64` objects, so if you are not using `numpy` types you need to do two way convertions every time you do a calculation.
  - the API is experimental.
  - it is a bit too complex if all you want is to calculate the number of business days between Jan-10 and Mar-25.
- `pandas`: another fantastic package, but again the functions operate on its own internal type and holidays are not quite handled yet.

## Example ##

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
	    (cal.busdaycount(date1, date2), date1, date2)

## License ##

MIT

## Developer ##

Antonio Botelho

## Last modification ##

11:15 PM Wednesday, December 11, 2013