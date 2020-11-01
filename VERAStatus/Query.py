"""
Query モジュール

データ要求に対する提供先を振り分ける
"""
from __future__ import annotations

import asyncio
from datetime import datetime

from . import Schedule as Sched
from . import SecZ
from .Server import ServerSettings
from .Utility import doy_string2datetime, get_now, async_execution


def get_status(doy_string: str, server_settings: ServerSettings):
    today = doy_string2datetime(doy_string)
    if today > get_now():
        raise RuntimeError('specified date ' + doy_string + ' is in future.')
    status_info = get_status_today(today, server_settings)
    return {
        'observation_info':
            Sched.info_list2lines_list(status_info['observation_info']),
        'secZ_info':
            SecZ.info_list2lines_list(status_info['secZ_info']),
    }


def get_status_today(today: datetime, server_settings: ServerSettings):
    task1 = asyncio.ensure_future(Sched.get_observations(today, today, server_settings))
    task2 = asyncio.ensure_future(SecZ.get(today, server_settings))
    obs_info_list, secz_info_list = async_execution([task1, task2])
    return {'observation_info': obs_info_list,
            'secZ_info': secz_info_list}


def get_status_today_synchronous(today: datetime, server_settings: ServerSettings):
    status = {'observation_info': Sched.get_observations(today, today, server_settings),
              'secZ_info': SecZ.get(today, server_settings)}
    # print(status)
    return status


def get_status_synchronous(date_from: datetime, date_until: datetime,
                           server_settings: ServerSettings):
    status = {'observation_info': Sched.get_observations(date_from, date_until, server_settings),
              'secZ_info': SecZ.get(date_from, server_settings)}
    # print(status)
    return status
