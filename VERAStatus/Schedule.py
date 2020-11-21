"""
Scheduleモジュール

観測スケジュール情報の一般的な扱いを行うモジュール。
個別観測スケジュールファイルについてはVexモジュール参照。
"""
from __future__ import annotations
from datetime import datetime
from typing import List

from .Server import ServerSettings
from .VERAStatus import Observations
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
                      server_settings: ServerSettings) -> Observations:
    with download_files_between(date_from, date_until, server_settings) as downloaded_file_paths_stat:
        return [make_observation_info(*file_info) for file_info in downloaded_file_paths_stat]


def sort_observations(obs_info_list: Observations) -> Observations:
    return sorted(obs_info_list, key=lambda info: info.start_time)


def get_observations(date_from: datetime, date_until: datetime, server_settings: ServerSettings
                     ) -> Observations:
    obs_info_list: Observations =\
        read_observations(date_from, date_until, server_settings)
    return sort_observations(obs_info_list)


def display_schedule(observations: Observations) -> None:
    print('===========\n  Schedule\n===========')
    if len(observations) == 0:
        print('no observations')
        return
    for observation in observations:
        print(observation.output_str + '-----------')
