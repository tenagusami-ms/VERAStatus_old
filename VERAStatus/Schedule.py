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
    """
    指定期間を含む日の観測情報
    Args:
        date_from(datetime.datetime): 開始日時
        date_until(datetime.datetime): 終了日時
        server_settings(ServerSettings): サーバ設定

    Returns:
        観測情報(Observations)
    """
    with download_files_between(date_from, date_until, server_settings) as downloaded_file_paths_stat:
        if len(downloaded_file_paths_stat) == 0:
            yield None
        else:
            for file_info in downloaded_file_paths_stat:
                yield make_observation_info(*file_info)


# def sort_observations(obs_info_list: Observations) -> Observations:
#     return sorted(obs_info_list, key=lambda info: info.start_time)


def get_observations(date_from: datetime, date_until: datetime,
                     server_settings: ServerSettings) -> Observations:
    obs_info_list: Observations =\
        read_observations(date_from, date_until, server_settings)
    # return sort_observations(obs_info_list)
    return obs_info_list


def display_schedule(observations: Observations) -> None:
    """
    観測の表示
    Args:
        observations(Observations): 観測リスト
    """
    print('===========\n  Schedule\n===========')
    # observations: Observations = next(observations_gen)
    for observation in observations:
        if observation is None:
            print(no_observation_str())
        else:
            print(observation.output_str + '-----------')


def no_observation_str() -> str:
    """
    観測がないときの表示
    Returns:
        観測なし表示文字列(str)
    """
    return '===========\n  Schedule\n===========\nno observations\n'
