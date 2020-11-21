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
from .Utility import doy_string2datetime, get_now, async_execution, incremented_day
from .VERAStatus import VERAStatus


def get_status(doy_string: str, server_settings: ServerSettings) -> VERAStatus:
    today = doy_string2datetime(doy_string)
    if today > get_now():
        raise RuntimeError('specified date ' + doy_string + ' is in future.')
    return get_status_today(today, server_settings)


def get_status_today(today: datetime, server_settings: ServerSettings) -> VERAStatus:
    task1 = asyncio.ensure_future(Sched.get_observations(today, today, server_settings))
    task2 = asyncio.ensure_future(SecZ.require_secz(today, server_settings))
    obs_info_list, secz_info_list = async_execution([task1, task2])
    return VERAStatus(obs_info_list, secz_info_list)


def get_status_today_synchronous(today: datetime, server_settings: ServerSettings) -> VERAStatus:
    return VERAStatus(Sched.get_observations(today, incremented_day(today), server_settings),
                      SecZ.require_secz(today, server_settings))


def get_status_synchronous(date_from: datetime, date_until: datetime,
                           server_settings: ServerSettings) -> VERAStatus:
    return VERAStatus(Sched.get_observations(date_from, date_until, server_settings),
                      SecZ.require_secz(date_from, server_settings))
