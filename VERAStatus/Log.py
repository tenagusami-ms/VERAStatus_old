import datetime as d

from .Utility import UTC


def time_string2datetime(time_string: str) -> d.datetime:
    date_tmp = d.datetime.strptime(time_string, '%Y%j%H%M%S')
    return d.datetime(
        date_tmp.year,
        date_tmp.month,
        date_tmp.day,
        date_tmp.hour,
        date_tmp.minute,
        date_tmp.second,
        tzinfo=UTC)


def datetime2doy_string(time: d.datetime) -> str:
    return time.strftime('%Y%j')


def datetime2time_string(time: d.datetime) -> str:
    return time.strftime('%Y%j%H%M%S')
