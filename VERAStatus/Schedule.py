"""
Scheduleモジュール

観測スケジュール情報の一般的な扱いを行うモジュール。
個別観測スケジュールファイルについてはVexモジュール参照。
"""
from __future__ import annotations
import dataclasses
import os
from datetime import datetime
from typing import List, Dict, Any

from .ObservationInfo import ObservationInfo
from .Server import ServerSettings, FileWithStat
from .Vex import make_observation_info, download_files_between


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


def read_observations(date_from: datetime, date_until: datetime,
                      server_settings: ServerSettings) -> List[ObservationInfo]:
    downloaded_file_paths_stat: List[FileWithStat] = \
        download_files_between(date_from, date_until, server_settings)
    observation_info_list: List[ObservationInfo] = \
        [make_observation_info(*file_info) for file_info in downloaded_file_paths_stat]
    for file_path, file_stat in downloaded_file_paths_stat:
        os.remove(file_path)
    return observation_info_list


def sort_observations(obs_info_list: List[ObservationInfo]) -> List[ObservationInfo]:
    return sorted(obs_info_list, key=lambda info: info['start_time'])


def get_observations(date_from: datetime, date_until: datetime, server_settings: ServerSettings):
    obs_info_list: List[ObservationInfo] =\
        read_observations(date_from, date_until, server_settings)
    return sort_observations(obs_info_list)


def info_list2lines_list(info_list: List[ObservationInfo]) -> List[List[str]]:
    def string_convert(info: ObservationInfo, item: str) -> str:
        info_dict: Dict[str, Any] = dataclasses.asdict(info)
        if item == 'start_time' or item == 'end_time':
            return f"{item}: {info_dict[item].astimezone().strftime('%m/%d(%jd) %H:%MJST')}"
        return f"{item}: {str(info_dict[item])}"

    def info2lines(info: ObservationInfo) -> List[str]:
        return [string_convert(info, item) for item in keywords()]

    if len(info_list) == 0:
        return [['no observations']]
    return [info2lines(info) for info in info_list]


def display(lines_list: List[List[str]]) -> None:
    print('===========\n  Schedule\n===========')
    for lines in lines_list:
        for line in lines:
            print(line)
        else:
            print('-----------')
