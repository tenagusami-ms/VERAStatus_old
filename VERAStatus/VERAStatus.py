"""
VERAStatus module

data records to be handled.
"""
from __future__ import annotations
__all__ = ["VERAStatus", "ObservationInfo", "Observations", "Weather", "SecZData"]

import dataclasses
from datetime import datetime
from functools import total_ordering
from typing import List, Generator, Optional

from VERAStatus.Utility import JST, wind_direction2octas


@dataclasses.dataclass
class VERAStatus:
    observations: Observations  # observation information
    secZ_list: List[SecZData]  # secZ information


@total_ordering
@dataclasses.dataclass(frozen=True)
class ObservationInfo:
    observation_ID: str  # 観測名
    description: str  # 観測のターゲット
    start_time: datetime  # 観測開始時刻
    end_time: datetime  # 観測終了時刻
    PI_name: str  # PI名
    contact_name: str  # コンタクト先
    band: str  # 観測バンド
    timestamp: datetime  # スケジュールファイルの最終更新時刻

    def __eq__(self, other):
        if not isinstance(other, ObservationInfo):
            return NotImplemented
        return self.start_time == other.start_time

    def __lt__(self, other):
        if not isinstance(other, ObservationInfo):
            return NotImplemented
        return self.start_time < other.start_time


    @property
    def output_str(self) -> str:
        if self.timestamp is None:
            timestamp_string: str = ""
        else:
            timestamp_string: str = f"timestamp: {datetime2display_time(self.timestamp)}\n"
        return f"observation ID: {self.observation_ID}\n" \
               f"description: {self.description}\n" \
               f"start time: {datetime2display_time(self.start_time)}\n" \
               f"end time: {datetime2display_time(self.end_time)}\n" \
               f"PI name: {self.PI_name}\n" \
               f"contact name: {self.contact_name}\n" \
               f"band: {self.band}\n" + timestamp_string


Observations = Generator[Optional[ObservationInfo], None, None]


@dataclasses.dataclass(frozen=True)
class SecZData:
    """
    secZ測定結果クラス
    """
    date_time: datetime  # 測定時刻
    optical_depth0: float  # 大気の光学的深さ0
    optical_depth1: float  # 大気の光学的深さ0
    atmospheric_temperature: float  # 気温(K)
    receiver_temperature: float  # 受信機雑音温度(K)
    system_temperature: float  # システム雑音温度(K)
    band: str  # 測定バンド
    misc: str  # その他
    weather: Weather  # 気象データ

    @property
    def output_str(self) -> str:
        return f"time: {datetime2display_time(self.date_time)}\n" \
               f"optical depth #1: {-self.optical_depth0:.2f}\n" \
               f"receiver temperature: {self.receiver_temperature:.0f}K\n" \
               f"system temperature: {self.system_temperature:.0f}K\n"\
               + self.weather.output_str


@total_ordering
@dataclasses.dataclass(frozen=True)
class Weather:
    """
    気象データ
    clock計算機のログの記載順
    """
    date_time: datetime  # データの日時
    wind_speed: float  # 風速(m/s)
    average_wind_speed: float  # 平均風速(m/s)
    max_wind_speed1: float  # 最大風速1(m/s)
    max_wind_speed2: float  # 最大風速2(m/s)
    wind_direction: float  # 風向(°)
    temperature1: float  # #1気温(℃)
    temperature2: float  # #2気温(℃)
    humidity1: float  # #1相対湿度(%)
    humidity2: float  # #2相対湿度(%)
    air_pressure: float  # 気圧(hPa)
    rain_flag: bool  # 雨が降っているかどうかのフラグ
    dhumidity1: float
    dhumidity2: float

    def __eq__(self, other):
        if not isinstance(other, Weather):
            return NotImplemented
        return self.date_time == other.date_time

    def __lt__(self, other):
        if not isinstance(other, Weather):
            return NotImplemented
        return self.date_time < other.date_time

    @property
    def output_str(self) -> str:
        return f"temperature #2(10m): {self.temperature2:.1f}℃\n" \
               f"relative humidity #2(10m): {self.humidity2:.0f}%\n" \
               f"air pressure: {self.air_pressure:.0f}hPa\n" \
               f"wind direction: {wind_direction2octas(self.wind_direction)}\n" \
               f"average wind speed: {self.average_wind_speed:.1f}m/s\n"


def datetime2display_time(date_time: datetime):
    return date_time.astimezone(JST).strftime('%m/%d(%jd) %H:%MJST')
