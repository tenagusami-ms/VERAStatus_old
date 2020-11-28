"""
Vexモジュール

vexスケジュールファイルから必要な情報を抜き出す。
"""
from __future__ import annotations

import re
from datetime import datetime, date
import pathlib as p
from typing import Dict, List, Union, Any, Optional, Match, Generator

from .Server import ServerSettings, download_files, FileStat, FileWithStat, get_command_output
from .Utility import UTC, egrep_command
from .VERAStatus import ObservationInfo


def vex_file_keywords() -> Dict[str, str]:
    """
    ObservationInfoクラス要素と、vexでのキーワードの対応の辞書
    Returns:
        対応辞書(Dict[str, str])
    """
    return {
        'observation_ID': 'exper_name',
        'description': 'exper_description',
        'start_time': 'exper_nominal_start',
        'end_time': 'exper_nominal_stop',
        'PI_name': 'PI_name',
        'contact_name': 'contact_name',
        'band': 'ref $IF'
    }


def download_files_between(date_start: datetime, date_end: datetime,
                           server_settings: ServerSettings) -> Generator[List[FileWithStat], None, None]:
    """
    指定された期間の日の間にある観測ファイルをサーバからダウンロードし、
    それらのファイル情報を返す。

    Note:
        期間終了日は含まない。

    Args:
        date_start(datetime.datetime): 期間開始日の任意の時刻
        date_end(datetime.datetime): 期間終了日の任意の時刻
        server_settings(ServerSettings): サーバ設定

    Returns:
        ダウンロードしたファイルの情報(List[FileWithStat])
    """
    downloaded_file_paths_stat: Generator[List[FileWithStat], None, None] = download_files(
        server_settings, server_settings.schedule_directory,
        path_predicate=lambda f: date_predicate(f, date_start.date(), date_end.date()))
    return downloaded_file_paths_stat


def schedule_files_between(date_start: datetime, date_end: datetime,
                           server_settings: ServerSettings) -> List[p.PurePath]:
    """
    サーバにある、指定された期間の日の間にある観測ファイルのリスト

    Note:
        date_end(期間終了日)は含まない。

    Args:
        date_start(datetime.datetime): 期間開始日の任意の時刻
        date_end(datetime.datetime): 期間終了日の任意の時刻
        server_settings(ServerSettings): サーバ設定

    Returns:
        スケジュールファイルリスト(List[pathlib.PurePath])
    """
    files: List[p.PurePath] = \
        [server_settings.schedule_directory / path for path
         in get_command_output(server_settings, f"ls {server_settings.schedule_directory}")
         if date_predicate(p.PurePosixPath(path), date_start.date(), date_end.date())]
    return files


def date_predicate(file: p.PurePath, date_start: date, date_end: date) -> bool:
    """
    観測ファイル名からわかる観測開始日が、指定された期間の日の間にあるかどうか
    Args:
        file(pathlib.PurePath): 観測ファイルパス
        date_start(datetime.datetime): 期間開始日の任意の時刻
        date_end(datetime.datetime): 期間終了日の任意の時刻

    Returns:
        期間開始時刻の日(date_from.date)<=観測名の日<期間終了時刻の日(date_end.date)ならTrue(bool)
        期間終了時刻の日は含まない。
    """
    try:
        observation_date = datetime.strptime(f"20{file.name[1:6]}", "%Y%j").date()
    except ValueError:
        return False
    return file.suffix == ".vex" and date_start <= observation_date < date_end


def make_observation_info(vex_file: p.Path, file_stat: FileStat) -> ObservationInfo:
    """
    vexファイルから、必要な観測情報が含まれる行の、キー・値ペアリストを抜き出す。
    Args:
        vex_file(p.Path): vexファイル
        file_stat(FileStat): ファイル情報

    Returns:
        キー・値ペアリスト(Dict[str, str])
    """
    with open(vex_file, 'r', encoding="utf-8", errors='ignore') as f:
        vex_file_lines: List[str] = f.readlines()
    obs_info_lines: Dict[str, Any] = extract_obs_info(vex_file_lines)
    return vex_lines2observation_info(obs_info_lines, file_stat)


# def receive_observation_info()


def extract_obs_info(vex_file_lines: List[str]) -> Dict[str, Any]:
    """
    vexファイルの行リストから、必要な観測情報が含まれる行の、キー・値の辞書を抜き出す。
    Args:
        vex_file_lines (List[str]): vexファイルの行リスト

    Returns:
        キー・値の辞書(Dict[str, Any])
    """
    comment_pattern = r'^\*'
    vex_lines: List[str] = [line for line in vex_file_lines
                            if not re.match(comment_pattern, line) and "=" in line]
    key_values: List[List[str]] = [[key_value.strip().strip(";").strip() for key_value
                                    in line.strip().split("=", 1)]
                                   for line in vex_lines]
    return {key: value for key, value in key_values if key in vex_file_keywords().values()}


def vex_time2datetime(time_string: str) -> datetime:
    """
    UTC時刻文字列をdatetimeにする。
    例えば20201026012345をdatetime(2020, 10, 26, 1, 23, 45, {UTC})にする。
    Args:
        time_string(str): UTC時刻文字列

    Returns:
        datetimeオブジェクト(datetime.datetime)
    """
    return datetime.strptime(time_string + "+0000", "%Yy%jd%Hh%Mm%Ss%z")


def vex_lines2observation_info(obs_info_lines: Dict[str, Any],
                               file_stat=None) -> ObservationInfo:
    """
    スケジュールから抜き出した観測情報辞書を、観測情報オブジェクトにする。
    Args:
        obs_info_lines(Dict[str, Any]): 観測情報辞書
        file_stat(FileStat, optional): スケジュールファイル情報

    Returns:
        観測情報(ObservationInfo)
    """

    def convert_value(vex_key: str) -> Union[str, datetime]:
        if vex_key == 'exper_nominal_start' or vex_key == 'exper_nominal_stop':
            return vex_time2datetime(obs_info_lines[vex_key])
        elif vex_key == 'ref $IF':
            matched: Optional[Match[str]] = re.search(r"^IF_([\w]+):", obs_info_lines[vex_key])
            if matched is None:
                return "unknown"
            return matched.groups()[0]
        return obs_info_lines.get(vex_key, None)

    observation_info_dict: Dict[str, Any] = \
        {observation_key: convert_value(vex_key)
         for observation_key, vex_key in vex_file_keywords().items()}
    if file_stat is not None:
        observation_info_dict["timestamp"] =\
            datetime.fromtimestamp(file_stat.st_mtime, tz=UTC)
    else:
        observation_info_dict["timestamp"] = None
    correct_names(observation_info_dict)
    return ObservationInfo(**observation_info_dict)


def schedule_file2observation_info(server_settings: ServerSettings,
                                   schedule_file: p.PurePath) -> ObservationInfo:
    """
    サーバ上のスケジュールファイルの内容を取得して観測情報にする
    Args:
        server_settings(ServerSettings): サーバ設定
        schedule_file(pathlib.PurePath): スケジュールファイルのサーバ上のパス

    Returns:
        観測情報(ObservationInfo)
    """
    lines: List[str] = get_command_output(
        server_settings,
        egrep_command(schedule_file, list(vex_file_keywords().values())))
    obs_info_lines: Dict[str, Any] = extract_obs_info(lines)
    return vex_lines2observation_info(obs_info_lines)


def correct_names(observation_info_dict: Dict[str, Any]) -> None:
    """
    観測情報辞書にPI情報がない（＝元のスケジュールに書いてない）などの
    特殊ケースへの対応のため、観測情報辞書のPI, コンタクト情報を修正する。
    Args:
        observation_info_dict(Dict[str, Any]): 観測情報辞書
    """
    if observation_info_dict["PI_name"] is None:
        if observation_info_dict["contact_name"] is None:
            observation_info_dict["contact_name"] = "unknown"
        observation_info_dict["PI_name"] = observation_info_dict["contact_name"]
    elif observation_info_dict["contact_name"] is None:
        observation_info_dict["contact_name"] = observation_info_dict["PI_name"]
