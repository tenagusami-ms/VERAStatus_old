"""
Weatherモジュール

気象データを扱う。
"""
from __future__ import annotations

__all__ = ["Weather", "require_weather_list", "log_file_weather_server",
           "query_command_weather_server"]

from datetime import datetime
import pathlib as p
from typing import Dict, List

from .Server import get_command_output, ServerSettings
from .Utility import datetime2doy_string, datetime2time_string, egrep_command_remote_remote

from .VERAStatus import Weather


def log_file_weather_server(date_time: datetime) -> p.PurePath:
    """
    時刻に対応する気象データサーバ(clock)上のログファイルパス
    Args:
        date_time(datetime.datetime): 時刻

    Returns:
        ログファイルパス(p.PurePath)
    """
    date_str: str = datetime2doy_string(date_time)
    return p.PurePosixPath("/usr2/log/days") / date_str / f"{date_str}.WS.log"


def query_command_weather_server(date_time_list: List[datetime]) -> str:
    """
    時刻リストから、気象ログの該当行を取得するための、気象データサーバ(clock)用コマンドを生成
    Args:
        date_time_list(List[datetime.datetime]): 時刻リスト

    Returns:
        コマンド(str)
    """
    time_str_list: List[str] = [datetime2time_string(date_time) for date_time in date_time_list]
    return egrep_command_remote_remote(
        log_file_weather_server(date_time_list[0]), time_str_list) + rf" | grep -v \;"


def uniq_lines(lines_raw: List[List[str]]) -> List[List[str]]:
    """
    気象データには同じ時刻が書かれたデータが複数ある場合があるので、
    時刻が同じ場合はあとの時刻だけを採用する。
    Args:
        lines_raw(List[List[str]]): 気象データの文字列リスト

    Returns:
        uniqされた気象データ文字列リスト
    """
    lines_dict: Dict[str, List[str]] = {line[0]: line[1:] for line in lines_raw}
    return [[time_str] + values for time_str, values in lines_dict.items()]


def require_weather_list(server_settings: ServerSettings, date_time_list: List[datetime]) -> List[Weather]:
    """
    時刻リストに対応する気象データリストをサーバから取得する。
    Args:
        server_settings: サーバ設定
        date_time_list: 時刻リスト

    Returns:
        気象データリスト(List[Weather])
    """
    if len(date_time_list) == 0:
        return list()
    lines_raw: List[List[str]] = \
        [line.split() for line
         in get_command_output(
            server_settings, "ssh clock -f " + query_command_weather_server(date_time_list))]
    lines: List[List[str]] = uniq_lines(lines_raw)
    return sorted([line2weather(line) for line in lines])


def line2weather(line: List[str]) -> Weather:
    """
    気象データ文字列リストを気象データにする
    Args:
        line(List[str]): 気象データ文字列リスト

    Returns:
        気象データ(Weather)
    """
    return Weather(datetime.strptime(line[0] + "+0000", "%Y%j%H%M%S%z"),
                   *[float(value) for value in line[1:11]],
                   bool(line[11]),
                   *[float(value) for value in line[12:]])
