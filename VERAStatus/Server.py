import dataclasses
from typing import List, Tuple, Dict

import paramiko as pa


FileStat = pa.SFTPAttributes
FileWithStat = Tuple[str, FileStat]


@dataclasses.dataclass
class ServerSettings:
    host: str  # サーバ
    user: str  # ユーザ名
    password: str  # パスワード


def server_settings_dict2settings(settings_dict: Dict[str, str]):
    return ServerSettings(settings_dict["host"], settings_dict["user"], settings_dict["password"])


def get_command_output(command: str, server_settings: ServerSettings) -> List[str]:
    with pa.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(pa.AutoAddPolicy())
        ssh.connect(
            hostname=server_settings.host,
            port=22,
            username=server_settings.user,
            password=server_settings.password)
        stdin, stdout, stderr = ssh.exec_command(command)
        return [f.split("\n")[0] for f in stdout]


def get_files(remote_dir: str, local_dir: str,
              server_settings: ServerSettings,
              path_predicate=lambda x: True) -> List[FileWithStat]:
    with pa.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(pa.AutoAddPolicy())
        ssh.connect(
            hostname=server_settings.host,
            port=22,
            username=server_settings.user,
            password=server_settings.password)
        with ssh.open_sftp() as sftp:
            try:
                sftp.chdir(remote_dir)
            except IOError:
                raise RuntimeError(
                    'the specified directory '
                    + remote_dir + 'does not exist.')
            remote_file_names: List[str] \
                = [file_name for file_name in sftp.listdir()
                   if path_predicate(file_name)]
            local_file_paths: List[str] = [local_dir + '/' + file_name
                                           for file_name in remote_file_names]
            remote_file_stat = []
            for remote_file_name, local_file_path \
                    in zip(remote_file_names, local_file_paths):
                sftp.get(remote_file_name, local_file_path)
                file_stat: pa.SFTPAttributes = sftp.stat(remote_file_name)
                remote_file_stat.append(file_stat)
            return list(zip(local_file_paths, remote_file_stat))
