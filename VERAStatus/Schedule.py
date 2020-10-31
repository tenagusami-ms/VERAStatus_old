import datetime as d
import os
from typing import List, Any, Tuple, Dict, Union

from . import vex as v
from ..utility import increment_day

ObsInfo = Dict[str, Union[str, d.datetime]]


def keywords() -> List[str]:
    return [
        'observation_ID',
        'description',
        'start_time',
        'end_time',
        'PI_name',
        'contact_name',
        'band',
        'timestamp',
    ]


def daily_boundary_from_0hUT() -> d.timedelta:
    return d.timedelta(hours=8)


def read_observations(date_from: d.datetime, date_until: d.datetime) -> List[ObsInfo]:
    transferred_file_paths_stat: List[Tuple[str, Any]] = v.get_files_between(date_from, date_until)
    observation_info_list: List[ObsInfo] = [
        v.read_obs_info(file_path, file_stat, keywords())
        for file_path, file_stat in transferred_file_paths_stat
    ]
    for file_path, file_stat in transferred_file_paths_stat:
        os.remove(file_path)
    return observation_info_list


def sort_observations(obs_info_list: List[ObsInfo]) -> List[ObsInfo]:
    return sorted(obs_info_list, key=lambda info: info['start_time'])


def filter_obs_today(obs_info_list: List[ObsInfo],
                     today: d.datetime,
                     time_delta: d.timedelta = d.timedelta(hours=0)
                     ) -> List[ObsInfo]:
    schedule_boundary_today: d.datetime = today + time_delta
    schedule_boundary_tomorrow: d.datetime = increment_day(schedule_boundary_today)

    def is_observation_today(info):
        return (info['start_time'] <= schedule_boundary_tomorrow
                and info['end_time'] > schedule_boundary_today)

    return [obs_info for obs_info in obs_info_list
            if is_observation_today(obs_info)]


def date_predicate(*args) -> bool:
    return v.date_predicate(*args)


def get_observations(date_from: d.datetime, date_until: d.datetime):
    obs_info_list: List[ObsInfo] = read_observations(date_from, date_until)
    return sort_observations(obs_info_list)


def info_list2lines_list(info_list: List[ObsInfo]) -> List[List[str]]:
    def string_convert(info: ObsInfo, item: str) -> str:
        if item == 'start_time' \
                or item == 'end_time':
            return item + ': ' \
                   + info[item].astimezone().strftime('%m/%d(%jd) %H:%MJST')
        return item + ': ' + str(info[item])

    def info2lines(info: ObsInfo) -> List[str]:
        return [string_convert(info, item) for item in keywords()]

    if not info_list:
        return [['no observations']]
    return [info2lines(info) for info in info_list]


def display(lines_list: List[str]) -> None:
    print('===========\n  Schedule\n===========')
    for lines in lines_list:
        for line in lines:
            print(line)
        else:
            print('-----------')
