"""
SecZ module

handling secz information
"""
from __future__ import annotations
__all__ = ["require_secz"]

from datetime import datetime
import pathlib as p
from typing import List, Tuple, Union, Generator

from . import Server as Serv
from .Log import extract_lines, line2data
from .Server import ServerSettings, get_command_output
from .VERAStatus import SecZData
from .Weather import Weather, require_weather_list


def display_secz(secz_list: List[SecZData]) -> None:
    """
    secZ測定ごとのデータをディスプレイ出力
    Args:
        secz_list(List[SecZData]): 各測定ごとのデータ
    """
    print('===========\n  sec Z\n===========')
    if len(secz_list) == 0:
        print('no sec Z data')
        return
    for secz_data in secz_list:
        print(secz_data.output_str + '-----------')


def remote_directory(date_time: datetime) -> p.PurePath:
    """
    リモートsecZデータディレクトリのパス
    Args:
        date_time(datetime.datetime): 日

    Returns:
        パス(pathlib.PurePosixPath)
    """
    return p.PurePosixPath("/") / "usr2" / "log" / "days" / date_time.strftime('%Y%j')


def remote_file_path(date_time: datetime) -> p.PurePath:
    """
    リモートsecZデータファイルのパス
    Args:
        date_time(datetime.datetime): ファイルが含む日時

    Returns:
        ファイルパス(pathlib.Path)
    """
    return remote_directory(date_time) / (date_time.strftime('%Y%j') + '.SECZ.log')


def require_secz(date_time: datetime, server_settings: ServerSettings) -> List[SecZData]:
    """
    指定された日時を含む日のSecZ測定結果リスト
    Args:
        date_time: 日時
        server_settings: サーバ設定

    Returns:
        SecZ測定結果(List[SecZData]]
    """
    file: p.PurePath = remote_file_path(date_time)
    with Serv.download_files(
            server_settings, file.parent,
            path_predicate=lambda fname: fname.name == file.name) as downloaded_file_path_stat:
        if len(downloaded_file_path_stat) == 0:
            return list()
        file_path, file_stat = next(iter(downloaded_file_path_stat))

        data_keyword: str = "TSYS1"
        with open(file_path, mode="r") as f:
            data_lines: List[Tuple[datetime, str]] = extract_lines(f.readlines(), data_keyword)
            weather_list: List[Weather] = \
                require_weather_list(server_settings, [date_time for date_time, _ in data_lines])
            return [data2secz(date_time, data_str_line, weather)
                    for (date_time, data_str_line), weather in zip(data_lines, weather_list)]


def data2secz(date_time: datetime, data_str_line: str, weather: Weather) -> SecZData:
    """
    secZログファイル内の時刻・値文字列と同時刻の気象データからsecZデータにする。
    Args:
        date_time(datetime.datetime): 時刻
        data_str_line(str): 値文字列
        weather(Weather): 気象データ

    Returns:
        secZデータ(SecZData)
    """
    data_str: List[str] = data_str_line.split()
    return SecZData(date_time,
                    float(data_str[0]),
                    float(data_str[1]),
                    float(data_str[2]),
                    float(data_str[3]),
                    float(data_str[4]),
                    data_str[5],
                    data_str[6],
                    weather)


def secz_query_command(date_time: datetime) -> str:
    """
    指定された日時を含む日のSecZ測定結果の問い合わせコマンド
    Args:
        date_time: 日時

    Returns:
        SecZ問い合わせコマンド(str)
    """
    data_keyword: str = "TSYS1"
    date_str: str = date_time.strftime("%Y%j")
    return rf"grep {data_keyword} /usr2/log/days/{date_str}/{date_str}.SECZ.log"


def acquire_secz_data(date_time: datetime, server_settings: ServerSettings
                      ) -> Generator[List[Union[datetime, str, float]], None, None]:
    """
    指定された日時を含む日のSecZ測定結果リスト
    Args:
        date_time(datetime.datetime): 日時
        server_settings(ServerSettings): サーバ設定

    Yields:
        測定結果リスト
    """
    for line in get_command_output(server_settings, secz_query_command(date_time)):
        date_time, _, data_str = line2data(line)
        yield [date_time, float(data_str[0]), float(data_str[1]), float(data_str[2]),
               float(data_str[3]), float(data_str[4]), data_str[5], data_str[6]]
    # data_line: List[Tuple[datetime, str, List[str]]] =\
    #     [line2data(line) for line in get_command_output(server_settings, secz_query_command(date_time))]


def assemble_secz_data() -> Generator[None, Union[List[Union[datetime, str, float]], Weather], SecZData]:
    """
    secZオブジェクトを組み立てるコルーチン
    Returns:
        secZオブジェクト(SecZData)
    """
    secz_data_list: List[Union[datetime, str, float, Weather]] = yield
    weather_data: Weather = yield
    secz_data_list.append(weather_data)
    return SecZData(*secz_data_list)


def generate_secz(date_time: datetime, server_settings: ServerSettings
                  ) -> List[SecZData]:
    """
    指定された日時を含む日のSecZオブジェクト
    Args:
        date_time(datetime.datetime): 日時
        server_settings(ServerSettings): サーバ設定

    Returns:

    """
    date_time_list: List[datetime] = list()
    secz_makers: List[Generator[None, Union[List[Union[datetime, str, float]], Weather], SecZData]] = list()

    for secz_data_list in acquire_secz_data(date_time, server_settings):
        secz_maker: Generator[None, Union[List[Union[datetime, str, float]], Weather], SecZData] =\
            assemble_secz_data()
        # secz_maker: Generator[None, Union[List[Union[datetime, str, float]], Weather], SecZData] = secz_maker_factory()
        next(secz_maker)
        secz_maker.send(secz_data_list)
        date_time_list.append(secz_data_list[0])
        secz_makers.append(secz_maker)

    secz_list: List[SecZData] = list()
    for weather, secz_maker in zip(require_weather_list(server_settings, date_time_list), secz_makers):
        try:
            secz_maker.send(weather)
            # secz_maker.send(None)
        except StopIteration as e:
            secz_list.append(e.value)

    return secz_list


def secz_maker_factory() -> Generator[None, Union[List[Union[datetime, str, float]], Weather], SecZData]:
    yield from assemble_secz_data()
