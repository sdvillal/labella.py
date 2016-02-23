
import arrow
import math

d3_date = arrow.Arrow
d3_time = {}

milli2arrow = lambda x : arrow.get(x / 1000.0)
arrow2milli = lambda x : x.float_timestamp * 1000.0

getTimezoneOffset = lambda x : x.utcoffset().total_seconds() / 60.0

class d3_time_interval():

    def __init__(self, local, step, number):
        self._local = local
        self._step = step
        self._number = number
        self.utc = d3_time_interval_utc(local)

    def round(self, date):
        d0 = self._local(date)
        d1 = self.offset(d0, 1)
        if date - d0 < d1 - date:
            return d0
        return d1

    def floor(self, date):
        return self._local(date)

    def ceil(self, date):
        ndate = self._local(milli2arrow(arrow2milli(date) - 1000))
        ndate = self._step(ndate, 1)
        return ndate

    def offset(self, date, k):
        ndate = arrow.Arrow(date)
        ndate = self._step(ndate, k)
        return ndate

    def range(self, t0, t1, dt):
#        import code
#        code.interact(local=dict(globals(), **locals()))
        time = self.ceil(t0)
        times = []
        if dt > 1:
            while time < t1:
                if not (self._number(time) % dt):
                    times.append(time.clone())
                time = self._step(time, 1)
        else:
            while time < t1:
                times.append(time.clone())
                time = self._step(time, 1)
        return times

    def range_utc(self, t0, t1, dt):
        try:
            d3_date = d3_date_utc
            utc = d3_date_utc()
            utc._ = t0
            return self.range(utc, t1, dt)
        finally:
            d3_date = arrow.Arrow

    def __call__(self, date):
        return self._local(date)

#def d3_time_interval(local, step, number):
#
#    def theround(date):
#        d0 = local(date)
#        d1 = offset(d0, 1)
#        if date - d0 < d1 - date:
#            return d0
#        return d1
#
#    def ceil(date):
#        ndate = local(arrow.Arrow(date - 1))
#        step(ndate, 1)
#        return ndate
#
#    def offset(date, k):
#        ndate = arrow.Arrow(date)
#        step(ndate, k)
#        return ndate
#
#    def therange(t0, t1, dt):
#        time = ceil(t0)
#        times = []
#        if dt > 1:
#            while time < t1:
#                if not (number(time) % dt):
#                    times.append(arrow.Arrow(time))
#                step(time, 1)
#        else:
#            while time < t1:
#                times.append(arrow.Arrow(time))
#                step(time, 1)
#        return times
#
#    def range_utc(t0, t1, dt):
#        try:
#            d3_date = d3_date_utc
#            utc = d3_date_utc()
#            utc._ = t0
#            return therange(utc, t1, dt)
#        finally:
#            d3_date = arrow.Arrow
#
#    local.floor = local
#    local.round = theround
#    local.ceil = ceil
#    local.offset = offset
#    local.range = therange
#
#    utc = d3_time_interval_utc(local)
#    local.utc = d3_time_interval_utc(local)
#    utc.floor = utc
#    utc.round = d3_time_interval_utc(theround)
#    utc.ceil = d3_time_interval_utc(ceil)
#    utc.offset = d3_time_interval_utc(offset)
#    utc.range = range_utc
#
#    return local

def d3_time_interval_utc(method):
    def func(date, k):
        try:
            d3_date = d3_date_utc
            utc = d3_date_utc()
            utc._ = date
            return method(utc, k)._
        finally:
            d3_date = arrow.Arrow
    return func

############ second ################################

d3_time['second'] = d3_time_interval(
        lambda date : milli2arrow(math.floor(arrow2milli(date) / 1e3) * 1e3),
        lambda date, offset : date.fromtimestamp((date.float_timestamp * 
            1000.0 + math.floor(offset) * 1e3)/1000.0),
        lambda date : date.second
        )

d3_time['seconds'] = d3_time['second'].range
d3_time['seconds_utc'] = d3_time['second'].range_utc

####################################################

############ minute ################################

d3_time['minute'] = d3_time_interval(
        lambda date : milli2arrow(math.floor(arrow2milli(date) / 6e4) * 6e4),
        lambda date, offset : date.fromtimestamp((date.float_timestamp * 
            1000.0  + math.floor(offset) * 6e4) / 1000.0),
        lambda date : date.minute
        )

d3_time['minutes'] = d3_time['minute'].range
d3_time['minutes_utc'] = d3_time['minute'].range_utc

####################################################

############ hour ##################################

def d3_time_hour_local(date):
    timezone = getTimezoneOffset(date) / 60
    ndate = milli2arrow((math.floor(arrow2milli(date) / 36e5 - timezone) + 
        timezone) * 36e5)
    return ndate

d3_time['hour'] = d3_time_interval(
        lambda date : d3_time_hour_local(date),
        lambda date, offset : milli2arrow(arrow2milli(date) + 
            math.floor(offset) * 36e5),
        lambda date : date.hour)

d3_time['hours'] = d3_time['hour'].range
d3_time['hours_utc'] = d3_time['hour'].range_utc

####################################################

############# day ##################################

d3_time['day'] = d3_time_interval(
        lambda date : arrow.Arrow(date.year, date.month, date.day),
        lambda date, offset : date.replace(day=(date.day + offset)),
        lambda date : date.day - 1
        )

d3_time['days'] = d3_time['day'].range
d3_time['days_utc'] = d3_time['day'].range_utc

d3_time['dayOfYear'] = (lambda date : math.floor((date - d3_time['year'](date) 
    - (getTimezoneOffset(date) - getTimezoneOffset(d3_time['year'])) * 6e4) / 
    864e5))

####################################################

########### week ###################################

def d3_time_week_local(date):
    # only sunday
    i = 7
    ndate = d3_time['day'](date)
    diff = ((date.isoweekday() % 7) + i) % 7
    ndate = arrow.get(ndate.float_timestamp - diff * 24 * 3600)
    return ndate

def d3_time_week_number(date):
    # only sunday
    i = 7
    day = d3_time['year'](date).isoweekday() % 7
    return (math.floor((d3_time['dayOfYear'](date) + (day + i) % 7) / 7) - 
            (day != i))

d3_time['week'] = d3_time_interval(
        lambda date : d3_time_week_local(date),
        lambda date, offset : arrow.get(date.float_timestamp + 
            math.floor(offset) * 7 * 24 * 3600),
        lambda date : d3_time_week_number(date)
        )

d3_time['weeks'] = d3_time['week'].range
d3_time['weeks_utc'] = d3_time['week'].range_utc

####################################################

############ month #################################

def d3_time_month_local(date):
    ndate = d3_time['day'](date)
    return ndate.replace(day=1)

def d3_time_month_offset(date, offset):
    nmonth = date.month + offset
    ndate = date.clone()
    while nmonth > 12:
        ndate = ndate.replace(year=ndate.year + 1)
        nmonth -= 12
    ndate = ndate.replace(month=nmonth)
    return ndate

d3_time['month'] = d3_time_interval(
        lambda date : d3_time_month_local(date),
        lambda date, offset : d3_time_month_offset(date, offset),
        lambda date : date.month - 1
        )

d3_time['months'] = d3_time['month'].range
d3_time['months_utc'] = d3_time['month'].range_utc

####################################################

############## year ################################

def d3_time_year_local(date):
    ndate = d3_time['day'](date)
    return ndate.replace(month=1, day=1)

d3_time['year'] = d3_time_interval(
        lambda date : d3_time_year_local(date),
        lambda date, offset : date.replace(year=date.year + offset),
        lambda date : date.year
        )

d3_time['years'] = d3_time['year'].range
d3_time['years_utc'] = d3_time['year'].range_utc

####################################################
