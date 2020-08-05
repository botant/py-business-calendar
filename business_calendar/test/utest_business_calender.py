from business_calendar import Calendar, MO, TU, WE, TH, FR, SA, SU, FOLLOWING, PREVIOUS, MODIFIEDFOLLOWING
from datetime import datetime
import pytest




# Verteilungsfunktion
def test_construction():
  cal = Calendar()
  assert type(cal) == Calendar
  assert cal.workdays == [MO, TU, WE, TH, FR]
  assert len(cal.weekdaymap) == 7

  cal = Calendar(workdays=[MO,WE,TH])
  assert type(cal) == Calendar
  assert cal.workdays == [MO,WE,TH]
  assert len(cal.weekdaymap) == 7

  cal = Calendar(workdays=[MO,TU,WE,TH], holidays=['2013-01-17'])
  assert type(cal) == Calendar
  assert cal.workdays == [MO,TU,WE,TH]
  assert cal.holidays == [datetime.strptime('17.01.2013', '%d.%m.%Y')]
  assert len(cal.weekdaymap) == 7


def test_range():
  start = "2019-12-31"
  end = "2020-01-07"
  busday_set = __gen_dt_set(["2019-12-31", "2020-01-01", "2020-01-02", "2020-01-03", "2020-01-06"])

  # test without holiday and with holiday
  # rotate the holiday(s)
  # use multiple holidays
  for cur_date in [[], ["2019-12-31"], ["2020-01-01"], ["2020-01-02"], ["2020-01-03"], ["2020-01-04"],
                  ["2020-01-05"], ["2020-01-06"], ["2019-12-31", "2020-01-01"], ["2019-12-31", "2020-01-06"],
                  ["2019-12-31", "2020-01-05"], ["2019-12-31", "2020-01-07"]]:
    cal = Calendar(holidays=cur_date)
    # remove the holiday from the busday_set
    eval_set = busday_set.difference(__gen_dt_set(cur_date))
    res_set = __gen_dt_set(cal.range(start, end))
    assert eval_set == res_set
    

def test_busdaycount():
  # start_day is ignored for calculation
  start = __gen_dt("2019-12-31")
  end = __gen_dt("2020-01-07")
  assert Calendar().busdaycount(start, end) == 5

  start = __gen_dt("2020-01-07")
  end = __gen_dt("2020-01-07")
  assert Calendar().busdaycount(start, end) == 0

  start = __gen_dt("2020-01-06")
  end = __gen_dt("2020-01-07")
  assert Calendar().busdaycount(start, end) == 1

  start = __gen_dt("2020-01-08")
  end = __gen_dt("2020-01-07")
  assert Calendar().busdaycount(start, end) == -1

  start = __gen_dt("2019-12-31")
  end = __gen_dt("2020-01-07")
  assert Calendar(holidays=["2019-12-31"]).busdaycount(start, end) == 5

  start = __gen_dt("2019-12-31")
  end = __gen_dt("2020-01-07")
  assert Calendar(holidays=["2019-12-31", "2020-01-04"]).busdaycount(start, end) == 5

  start = __gen_dt("2019-12-31")
  end = __gen_dt("2020-01-07")
  assert Calendar(workdays=[MO, WE], holidays=["2019-12-31"]).busdaycount(start, end) == 2

  start = __gen_dt("2019-12-31")
  end = __gen_dt("2020-01-07")
  assert Calendar(holidays=["2019-12-31", "2020-01-11"]).busdaycount(start, end) == 5

  # 2019-12-31 is TU
  # 2020-01-01 is WE
  # ...
  # 2020-01-07 is TU
  start = __gen_dt("2019-12-31")
  end = __gen_dt("2020-01-07")
  assert Calendar(workdays=[MO], holidays=["2020-01-06"]).busdaycount(start, end) == 0

  start = "2019-12-31"
  end = "2020-01-07"
  busday_set = __gen_dt_set(["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"])

  # test without holiday and with holiday
  # rotate the holiday(s)
  # use multiple holidays
  for cur_date in [[], ["2019-12-31"], ["2020-01-01"], ["2020-01-02"], ["2020-01-03"], ["2020-01-04"],
                  ["2020-01-05"], ["2020-01-06"], ["2020-01-07"], ["2019-12-31", "2020-01-01"], 
                  ["2019-12-31", "2020-01-06"], ["2019-12-31", "2020-01-05"], ["2019-12-31", "2020-01-07"]]:
    cal = Calendar(holidays=cur_date)
    # remove the holiday from the busday_set
    eval_len = len(busday_set.difference(__gen_dt_set(cur_date)))
    res_len = cal.busdaycount(start, end)
    assert eval_len == res_len


# #################################
# helper functions
# #################################

def __gen_dt(date):
  """Taken from source code"""
  """Simple date parsing function"""
  if hasattr(date, 'year'):
    return date
  try:
    return datetime.strptime(date, '%Y-%m-%d')
  except ValueError:
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

def __gen_dt_set(str_date_list):
  return {__gen_dt(d) for d in str_date_list}
