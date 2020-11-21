"""
Logモジュール

観測ログを扱う。
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Tuple

from VERAStatus.Utility import time_string2datetime


def extract_lines(lines: List[str], key: str) -> List[Tuple[datetime, str]]:
    """
    ログファイルの行から、キーが一致する行の時刻と値文字列を取り出す
    Args:
        lines(Line[str]): ログファイルの行リスト
        key(str): キー

    Returns:
        時刻・値文字列タプルのリスト
    """
    line_candidates: List[List[str]] = \
        [line.strip().split("/") for line in lines if key in line]
    return [(time_string2datetime(time_str.strip()), value.strip())
            for time_str, keyword, value in line_candidates if keyword == key]
