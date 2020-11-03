from datetime import date
import pathlib as p

from VERAStatus.SecZ import remote_directory, remote_file_name


def test_remote_directory():
    assert remote_directory(date(2020, 10, 26)) == p.PurePosixPath("/usr2/log/days/2020300")


def test_remote_file_name():
    assert remote_file_name(date(2020, 10, 26)) == "2020300.SECZ.log"
