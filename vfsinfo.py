"""Overview:
    vfsinfo.py : test for vfs data acquisition

Usage:
    vfsinfo.py [-d YYYYJJJ | --date YYYYJJJ] [-s file | --setting file]

    vfsinfo.py -h | --help

Options:
    -d, --date YYYYJJJ  : doy JJJ in year YYYY for data acquisition.
    -s, --setting file     : the path to the setting file
    -h --help          : Show this screen and exit.

"""
from __future__ import annotations

import dataclasses
from datetime import datetime
import pathlib as p
import sys
from typing import Any, Dict

from docopt import docopt
from schema import Schema, And, Use, Or, SchemaError

import VERAStatus.Schedule as Sched
import VERAStatus.SecZ as SecZ
from VERAStatus.Query import get_status_today_synchronous
from VERAStatus.Server import ServerSettings, server_settings_dict2settings
from VERAStatus.Utility import DataReadError, read_json, Error


def main() -> None:
    """
    Main Procedure
    """
    try:
        options: Options = read_options()
        server_setting: ServerSettings = \
            server_settings_dict2settings(read_json(options.setting_file)["VLBI"])
        today: datetime = options.date
        # # info = q.get_status_today(today)
        info = get_status_today_synchronous(today, server_setting)

        Sched.display(Sched.info_list2lines_list(info['observation_info']))
        SecZ.display(SecZ.info_list2lines_list(info['secZ_info']))
    except Error as e:
        print(e.args[0])
        sys.exit(1)


@dataclasses.dataclass
class Options:
    """
    オプション格納
    """
    date: datetime  # 観測情報取得日
    setting_file: p.Path


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
                                         + f" is not in YYYYJJJ form.\n"))),
        "--setting": Or(None, And(Use(p.Path), lambda path: path.is_file(),
                                  error=f"The specified file {args['--setting']}"
                                        + " does not exist.\n")),
    })

    try:
        args = schema.validate(args)
        if args["--date"] is None:
            args["--date"] = datetime.utcnow()
        if args["--setting"] is None:
            default_setting: p.Path = p.Path(__file__).parent.parent / "work" / "settings.json"
            if not default_setting.is_file():
                raise DataReadError(f"The default setting file {default_setting} does not exist.")
            args["--setting"] = default_setting

    except SchemaError as e:
        print(e.args[0])
        exit(1)

    return Options(args["--date"], args["--setting"])


if __name__ == '__main__':
    main()
    sys.exit(0)
