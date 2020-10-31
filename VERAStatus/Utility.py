import copy
import datetime as d
import json
from decimal import Decimal, ROUND_HALF_UP
import tempfile
from functools import reduce
from typing import Tuple, List, TypeVar, Dict, Any

from openpyxl import Workbook
import asyncio

T = TypeVar("T")


class Error(Exception):
    """
    パッケージの例外基本クラス
    """
    pass


class DataReadError(Error):
    """
    データ読み出し失敗の例外クラス
    """
    pass


class DataWriteError(Error):
    """
    データ書き込み失敗の例外クラス
    """
    pass


class UsageError(Error):
    """
    関数の使用法が誤っているエラー
    """
    pass


class ProcessError(Error):
    """
    呼び出した実行プロセスが失敗したエラー
    """
    pass


def read_json(json_file) -> Dict[str, Any]:
    """
    JSONファイルを読み出す
    Args:
        json_file: JSONファイル

    Returns:
        JSON辞書

    Raises:
        DataReadError: データ読み出し失敗
    """
    try:
        with open(json_file, "r") as f:
            return json.load(f)
    except OSError:
        raise DataReadError(f"data readout failed: {json_file} (module {__name__}).")


def jst() -> d.timezone:
    return d.timezone('Asia/Tokyo')


def in_jst(datetime):
    return d.timezone('Asia/Tokyo').localize(datetime)


def utc_timezone() -> d.tzinfo:
    return d.timezone(d.timedelta(0))


def tmp_dir():
    return tempfile.gettempdir()


def increment_day(day) -> d.datetime:
    return day + d.timedelta(days=1)


def decrement_day(day) -> d.datetime:
    return day + d.timedelta(days=-1)


def round_float(r: float, order: float) -> float:
    rounded: Decimal = Decimal(float(r)).quantize(
        Decimal(str(order)), rounding=ROUND_HALF_UP)
    if order > 0.1:
        return int(rounded)
    return float(rounded)


def doy2datetime(year: int, doy: int) -> d.datetime:
    return doy_string2datetime(str(year)+str(doy))


def doy_string2datetime(doy_string) -> d.datetime:
    date_tmp: d.datetime = d.datetime.strptime(doy_string + '+0000', '%Y%j%z')
    return datetime_at_0h(datetime2utc(date_tmp))


def datetime2year_doy_string(today: d.datetime) -> Tuple[str, str]:
    return today.strftime('%Y'), today.strftime('%j')


def datetime2year_doy(today: d.datetime) -> Tuple[int, int]:
    return today.year, int(today.strftime('%j'))


def datetime2doy_string(today: d.datetime) -> str:
    year, doy = datetime2year_doy_string(today)
    return year + doy


def datetime2doy(today: d.datetime) -> int:
    return int(today.strftime('%j'))


def string_lines2string(string_lines: List[str]) -> str:
    return reduce(lambda ss, s: ss + s + '\n', string_lines, '')


def get_now() -> d.datetime:
    date_tmp: d.datetime = d.datetime.now(d.timezone.utc)
    return datetime2utc(date_tmp)


def is_offset_naive_datetime(datetime_obj: d.datetime) -> bool:
    return not datetime_obj.tzinfo


def datetime2utc(date_tmp: d.datetime) -> d.datetime:
    if date_tmp.tzinfo != d.timezone.utc:
        return date_tmp.astimezone(d.timezone.utc)
    return date_tmp


def datetime_at_0h(date_tmp) -> d.datetime:
    return d.datetime(
        date_tmp.year, date_tmp.month, date_tmp.day, tzinfo=date_tmp.tzinfo)


def make_out_data_matrix(title_row, in_data_matrix: List[List[T]]):
    # out_matrix = [[row[item] for item in title_row] for row in in_data_matrix]
    out_matrix: List[List[T]] = copy.deepcopy(in_data_matrix)
    out_matrix.insert(0, title_row)
    return out_matrix


def excel_file_out(file_path: str, sheet_title: str, data_matrix: List[List[T]]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_title
    for data_row in data_matrix:
        ws.append(data_row)
    wb.save(file_path)


def async_execution(tasks):
    loop = asyncio.get_event_loop()
    future = asyncio.gather(*tasks)
    loop.run_until_complete(future)
    return future.result()


def columnize(row_string, splitter):
    return [value_string.strip() for value_string
            in row_string.strip().split(splitter)]


def coefficient_Torr2Pa():
    return 101325.0/760.0
