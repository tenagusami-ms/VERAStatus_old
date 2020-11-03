"""
Serverモジュール

スケジュール・気象データアクセスサーバ(たいていoperation)へのsshアクセスを行う。
"""
from __future__ import annotations
import dataclasses
import os
import pathlib as p
import tempfile
from contextlib import contextmanager
from typing import List, Tuple, Dict, Any, Generator

import paramiko as pa
from paramiko import SSHException, AuthenticationException

from VERAStatus.Utility import DataReadError

FileStat = pa.SFTPAttributes
FileWithStat = Tuple[p.Path, FileStat]


@dataclasses.dataclass(frozen=True)
class ServerSettings:
    """
    サーバ設定のクラス
    """
    host: str  # サーバ
    port: int  # ポート
    user: str  # ユーザ名
    password: str  # パスワード
    schedule_directory: p.PurePath  # サーバ上のパス


def server_settings_dict2settings(settings_dict: Dict[str, Any]) -> ServerSettings:
    """
    設定辞書を設定クラスに格納
    Args:
        settings_dict(Dict[str, Any]: 設定辞書

    Returns:
        設定クラス(ServerSettings)
    """
    return ServerSettings(settings_dict["host"],
                          int(settings_dict["port"]),
                          settings_dict["user"],
                          settings_dict["password"],
                          p.PurePosixPath(settings_dict["schedule_path"]))


def get_command_output(server_settings: ServerSettings, command: str) -> List[str]:
    """
    サーバ上でコマンドを走らせて出力を得る
    Args:
        server_settings(ServerSettings): サーバ設定
        command(Str): コマンド

    Returns:
        改行でsplitされたコマンド出力(List[str])

    Raises:
        DataReadError: 接続失敗
    """
    try:
        with pa.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(pa.AutoAddPolicy())
            ssh.connect(hostname=server_settings.host,
                        port=server_settings.port,
                        username=server_settings.user,
                        password=server_settings.password)
            stdin, stdout, stderr = ssh.exec_command(command)
            # print(command, stdout)
            return [f.split("\n")[0] for f in stdout]
    except (SSHException, AuthenticationException, IOError) as e:
        raise DataReadError(e.args[0])


@contextmanager
def download_files(server_settings: ServerSettings,
                   remote_directory: p.PurePath,
                   local_directory=p.Path(tempfile.gettempdir()),
                   path_predicate=lambda x: True) -> Generator[List[FileWithStat], None, None]:
    """
    サーバ上からファイルをダウンロードする
    Args:
        server_settings(ServerSettings): サーバ設定
        remote_directory(pathlib.PurePath): リモートディレクトリ
        local_directory (pathlib.Path, optional): ローカルディレクトリ。デフォルトはOSのテンポラリディレクトリ。
        path_predicate(Callable[[p.PurePath], bool], optional): ファイル名フィルタ関数。デフォルトはTrueの定数関数。

    Returns:
        ダウンロードしたファイル情報(List[FileWithStat])

    Raises:
        DataReadError: 接続失敗
    """
    downloaded_files: List[FileWithStat] = []
    try:
        with pa.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(pa.AutoAddPolicy())
            ssh.connect(
                hostname=server_settings.host,
                port=server_settings.port,
                username=server_settings.user,
                password=server_settings.password)
            with ssh.open_sftp() as sftp:
                sftp.chdir(str(remote_directory))
                remote_file_names: List[str] = [p.PurePath(file).name for file in sftp.listdir()
                                                if path_predicate(p.PurePath(file))]
                downloaded_files: List[FileWithStat] = []
                for remote_file_name in remote_file_names:
                    local_file: p.Path = local_directory / remote_file_name
                    sftp.get(remote_file_name, local_file)
                    file_stat: pa.SFTPAttributes = sftp.stat(remote_file_name)
                    downloaded_files.append((local_file, file_stat))
                yield downloaded_files

    except (SSHException, AuthenticationException, IOError) as e:
        raise DataReadError(e.args[0])
    finally:
        for file, _ in downloaded_files:
            if file.is_file():
                os.remove(file)
