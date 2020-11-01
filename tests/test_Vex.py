from datetime import date, datetime
import pathlib as p
from typing import List

import pytest

from VERAStatus.Utility import UTC
from VERAStatus.Vex import time_string2datetime, date_predicate


@pytest.mark.parametrize('observation_id, start_date, end_date, expected', [
    (p.PurePath("r20300a.vex"), [2020, 10, 26], [2020, 10, 27], True),
    (p.PurePath("./r20300ab.vex"), [2020, 10, 25], [2020, 10, 27], True),
    (p.PurePath("f20300a.vex"), [2020, 10, 25], [2020, 10, 26], False),
    (p.PurePath("fd20300a.vex"), [2020, 10, 25], [2020, 10, 26], False),
])
def test_date_predicate(observation_id: p.PurePath, start_date: List[int],
                        end_date: List[int], expected: bool):
    assert date_predicate(observation_id, date(*start_date), date(*end_date)) == expected


def test_time_string2datetime():
    assert time_string2datetime("2020y300d01h23m45s") == datetime(2020, 10, 26, 1, 23, 45, tzinfo=UTC)
