"""
Weatherモジュール

気象データを扱う。
"""
from __future__ import annotations
from datetime import datetime, tzinfo
import math
from typing import Union, Dict, List

from .Server import get_command_output, ServerSettings
from .Utility import round_float, datetime2doy_string, datetime2time_string, time_string2datetime

WeatherData = Union[str, int, float, bool, datetime]
Weather = Dict[str, WeatherData]


def data_keywords() -> List[str]:
    return [
        'time',
        'wind_speed',
        'average_wind_speed',
        'max_wind_speed1',
        'max_wind_speed2',
        'wind_direction',
        'temperature1',
        'temperature2',
        'humidity1',
        'humidity2',
        'air_pressure',
        'rain_flag',
        'dhumidity1',
        'dhumidity2',
    ]


def out_items() -> List[str]:
    return [
        'temperature1',
        'humidity1',
        'temperature2',
        'humidity2',
        'air_pressure',
        'average_wind_speed',
        'wind_direction',
    ]


def wind_direction2octas(direction_degree: float) -> str:
    """
    風向の角度から八方位にする。
    Args:
        direction_degree(float): 風向の方位角(度)。北を0°としたCW方向。

    Returns:
        八方位の文字列(str)
    """
    if direction_degree >= 360.0 or direction_degree < 0.0:
        direction_degree = direction_degree \
            - float(math.floor(direction_degree / 360.0 + 1.e-8)) * 360.0
    direction_degree_shift = direction_degree + 360.0 / 16.0
    if direction_degree_shift < 45.0:
        return 'N'
    if direction_degree_shift < 90.0:
        return 'NE'
    if direction_degree_shift < 135.0:
        return 'E'
    if direction_degree_shift < 180.0:
        return 'SE'
    if direction_degree_shift < 225.0:
        return 'S'
    if direction_degree_shift < 270.0:
        return 'SW'
    if direction_degree_shift < 315.0:
        return 'W'
    return 'NW'


def find_data(time: datetime, server_settings: ServerSettings) -> Weather:
    data_list: List[Weather] = make_data(time, server_settings)
    timedelta_array: List[tzinfo] = [abs(data['time'] - time) for data in data_list]
    min_index: int = timedelta_array.index(min(timedelta_array))
    return data_list[min_index]


def get_data(time: datetime, server_settings: ServerSettings, keywords=None) -> Weather:
    if keywords is None:
        keywords: List[str] = data_keywords()
    data: Weather = find_data(time, server_settings)
    return {key: value for key, value in data.items() if key in keywords}


def make_query_command(time: datetime) -> str:
    date_string: str = datetime2doy_string(time)
    time_string: str = datetime2time_string(time)[0:-2]
    return 'ssh clock -f "grep ' + time_string + ' /usr2/log/days/' \
        + date_string + '/' + date_string + '.WS.log |grep -v SPDNOW"'


def get_log_lines(time: datetime, server_settings: ServerSettings) -> List[str]:
    return get_command_output(server_settings, make_query_command(time))


def make_data(time: datetime, server_settings: ServerSettings) -> List[Weather]:
    def convert_value(item: str, value) -> WeatherData:
        if item == 'time':
            return time_string2datetime(value)
        if item == 'rain_flag':
            if float(value) == 0:
                return False
            else:
                return True
        if item == 'air_pressure' \
           or item == 'humidity1' \
           or item == 'humidity2':
            return int(round_float(float(value), 0))
        if item == 'wind_direction':
            return wind_direction2octas(float(value))
        return round_float(float(value), -1)

    log_lines: List[str] = get_log_lines(time, server_settings)
    return [{
        item: convert_value(item, value)
        for (item, value) in zip(data_keywords(), line.split())
    } for line in log_lines]
