"""Overview:
    HydrogenMaser.py : get the status of the hydrogen maser

Usage:
    HydrogenMaser.py [--setting file]

    HydrogenMaser.py -h | --help

Options:
    --setting file  : the path to the setting file
    -h --help       : Show this screen and exit.

"""
import dataclasses
import sys
from datetime import date, time, datetime
import pathlib as p
from typing import Dict, Any

from docopt import docopt
from schema import Schema, Or, And, Use, SchemaError

from VERAStatus.HydrogenMaserServer import report_parameters, get, MaserSettings, read_settings
from VERAStatus.Utility import in_jst, Error, DataReadError, read_json


def main() -> None:
    """
    Main Procedure
    """
    try:
        options: Options = read_options()
        settings: MaserSettings = \
            read_settings(read_json(options.setting_file)["H_maser_settings"])

        status = get(settings, in_jst(datetime.combine(date.today(), time())))
        for param in report_parameters():
            print(param['label'] + ':',
                  status[-1][param['label']], param['unit'])

    except Error as e:
        print(e.args[0])
        sys.exit(1)


@dataclasses.dataclass
class Options:
    """
    オプション格納
    """
    setting_file: p.Path


def read_options() -> Options:
    """
    コマンドラインオプションの設定を読む。

    Returns:
        オプション設定(Options)
    """
    args: Dict[str, Any] = docopt(__doc__)
    schema = Schema({
        "--setting": Or(None, And(Use(p.Path), lambda path: path.is_file(),
                                  error=f"The specified file {args['--setting']}"
                                        + " does not exist.\n")),
    })

    try:
        args = schema.validate(args)
        if args["--setting"] is None:
            default_setting: p.Path = p.Path(__file__).parent.parent / "work" / "settings.json"
            if not default_setting.is_file():
                raise DataReadError(f"The default setting file {default_setting} does not exist.")
            args["--setting"] = default_setting

    except SchemaError as e:
        print(e.args[0])
        exit(1)

    return Options(args["--setting"])


if __name__ == '__main__':
    main()
    sys.exit(0)
