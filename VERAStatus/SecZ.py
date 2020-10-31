from datetime import datetime
import os
from typing import List
from . import Log
from . import Server as Serv
from .Server import ServerSettings
from .Utility import round_float, tmp_dir
from .Weather import get_data, Weather


def keywords() -> List[str]:
    return [
        'optical_depth_0', 'optical_depth_1', 'atmospheric_temperature',
        'receiver_temperature', 'system_temperature', 'band', 'misc'
    ]


def out_keywords() -> List[str]:
    return [
        'time',
        'optical_depth_0',
        'receiver_temperature',
        'system_temperature',
        'band',
    ]


def weather_keywords() -> List[str]:
    return [
        'temperature2',
        'humidity2',
        'air_pressure',
        'wind_direction',
        'average_wind_speed',
    ]


def add_weather_data(info, server_settings: ServerSettings):
    weather_data = get_data(info['time'], server_settings, weather_keywords())
    info.update(weather_data)
    return info


def get(today: datetime, server_settings: ServerSettings):
    return [add_weather_data(info, server_settings) for info in read(today, server_settings)]


def info_list2lines_list(info_list):
    def string_convert(info, item):
        if item == 'time':
            return item + ': ' \
                + info[item].astimezone().strftime('%m/%d(%jd) %H:%MJST')
        return item + ': ' + str(info[item])

    def info2lines(info):
        return [string_convert(info, item) for item
                in out_keywords() + weather_keywords()]

    if not info_list:
        return [['no secZ data']]
    return [info2lines(info) for info in info_list]


def display(lines_list):
    print('===========\n  sec Z\n===========')
    if not lines_list:
        print('no sec Z data')
        return
    for lines in lines_list:
        for line in lines:
            print(line)
        else:
            print('-----------')


def remote_dir(today):
    return '/usr2/log/days' + '/' + today.strftime('%Y%j')


def remote_file_name(today):
    return today.strftime('%Y%j') + '.SECZ.log'


def make_data(line: List[str]) -> Weather:
    def convert_value(keyword: str, value: float) -> float:
        if keyword == 'optical_depth_0':
            value = -round_float(value, 0.01)
        elif not keyword == 'band':
            value = int(round_float(value, 0))
        return value

    data_dict_tmp: Weather = {
        keyword: convert_value(keyword, value)
        for (keyword, value) in zip(keywords(), line[2].split())
    }
    data_dict_tmp['time'] = Log.time_string2datetime(line[0])
    return {
        keyword: value
        for keyword, value in data_dict_tmp.items()
        if keyword in out_keywords()
    }


def read(today: datetime, server_settings: ServerSettings):
    try:
        file_name: str = remote_file_name(today)
        file_path, file_stat = Serv.get_files(
            remote_dir(today), tmp_dir(),
            server_settings,
            lambda fname: fname == file_name)[0]
    except (RuntimeError, IndexError):
        return []

    data_keyword: str = 'TSYS1'
    with open(file_path, 'r') as f:
        lines: List[List[str]] = [[
            key_value.strip().strip(";") for key_value in line.strip().split("/")
        ] for line in f.readlines() if data_keyword in line]
    os.remove(file_path)
    return [make_data(line) for line in lines]
