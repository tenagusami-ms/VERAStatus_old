from datetime import datetime
import pathlib as p

from VERAStatus.Utility import UTC
from VERAStatus.Weather import wind_direction2octas, log_file_weather_server, query_command_weather_server


def test_wind_direction2octas():
    assert wind_direction2octas(45.0) == "NE"
    assert wind_direction2octas(-50.0) == "NW"
    assert wind_direction2octas(500.0) == "SE"


def test_log_file_weather_server():
    assert log_file_weather_server(datetime(2020, 10, 26, 10, 30, 30)) == \
           p.PurePosixPath("/usr2/log/days") / "2020300.WS.log"


def test_query_command_weather_server():
    assert query_command_weather_server(
        [datetime(2020, 11, 21, 11, 30, 0).astimezone(UTC),
         datetime(2020, 11, 21, 11, 30, 1).astimezone(UTC)]) == \
           r'egrep "\"2020326023000|2020326023001"\" /usr2/log/days/2020326.WS.log | ' \
           + r'grep -v \;'
