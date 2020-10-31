"""Overview:
    vfsinfo.py : test for vfs data acquisition

Usage:
    vfsinfo.py [--date YYYYJJJ]

    vfsinfo.py -h | --help

Options:
    --date YYYYJJJ  : doy JJJ in year YYYY for data acquisition.
    -h --help       : Show this screen and exit.

"""
from __future__ import annotations

import dataclasses
from datetime import datetime
import pathlib as p
from re import match
import sys
from typing import Any, Dict

from docopt import docopt
from schema import Schema, And, Use, Or, SchemaError

# import VERAStatus.Schedule as Sched
# import VERAStatus.SecZ as SecZ
# from VERAStatus.Query import get_status_today_synchronous
from VERAStatus.Utility import datetime_at_0h, datetime2utc, get_now


def main() -> None:
    """
    Main Procedure
    """
    options: Options = read_options()
    print(options)
    # today = option_dict['date']
    # # info = q.get_status_today(today)
    # info = get_status_today_synchronous(today)

    # Sched.display(Sched.info_list2lines_list(info['observation_info']))
    # SecZ.display(SecZ.info_list2lines_list(info['secZ_info']))


@dataclasses.dataclass
class Options:
    """
    オプション格納
    """
    date: datetime  # 観測情報取得日


def read_options() -> Options:
    """
    コマンドラインオプションの設定を読む。

    Returns:
        オプション設定(Options)
    """
    args: Dict[str, Any] = docopt(__doc__)
    schema = Schema({
        "--date": Or(None, And(Use(lambda s: datetime.strptime(s + "+0000", "%Y%j%z"),
                                   error=f"The specified date {args['--date']}"
                                         + f" is not in YYYYJJJ form.\n")))
    })

    try:
        args = schema.validate(args)
        if args["--date"] is None:
            args["--date"] = datetime.utcnow()
    except SchemaError as e:
        print(e.args[0])
        exit(1)

    return Options(args["--date"])


if __name__ == '__main__':
    main()
