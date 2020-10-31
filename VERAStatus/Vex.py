import datetime as d
import re
from typing import Dict, List, Any, KeysView, Tuple

from .. import operation as oper
from .. import utility as u


def vex_keywords() -> Dict[str, str]:
    return {
        'exper_name': 'observation_ID',
        'exper_description': 'description',
        'exper_nominal_start': 'start_time',
        'exper_nominal_stop': 'end_time',
        'PI_name': 'PI_name',
        'contact_name': 'contact_name',
        'ref $IF': 'band',
    }


def time_string2time(time_string: str) -> d.datetime:
    date_tmp = d.datetime.strptime(time_string, '%Yy%jd%Hh%Mm%Ss')
    return d.datetime.combine(date_tmp.date(), date_tmp.time(),
                              u.utc_timezone())


def vex_dir() -> str:
    return '/usr2/sched/vex'


def get_files(today: d.datetime) -> List[Tuple[str, Any]]:
    return get_files_between(today, today)


def get_files_between(date_from: d.datetime, date_until: d.datetime
                      ) -> List[Tuple[str, Any]]:
    schedule_file_pattern: str = r'^(\w\d{5}\w*).vex$'

    def file_predicate(file_name: str) -> bool:
        if re.match(schedule_file_pattern, file_name):
            observation_ID_string: str = re.search(
                schedule_file_pattern, file_name).group(1)
            return date_predicate(observation_ID_string, date_from, date_until)
        return False

    return oper.get_files(vex_dir(), u.tmp_dir(), file_predicate)


def date_predicate(observation_id: str, date_from: d.datetime, date_until: d.datetime) -> bool:
    year_doy_num_from: int = int(u.datetime2doy_string(date_from)[2:])
    year_doy_num_until: int = int(u.datetime2doy_string(date_until)[2:])
    ID_pattern: str = r'^\w(\d{5})\w*'
    if re.match(ID_pattern, observation_id):
        year_doy_num: int = int(re.search(ID_pattern, observation_id).group(1))
        return year_doy_num_from <= year_doy_num <= year_doy_num_until
    return False


def make_keyword_dict(keywords: List[str]) -> Dict[str, str]:
    return {vex_key: key for vex_key, key in zip(vex_keywords(), keywords)}


def read_obs_info(file_path: str, file_stat: oper.FileStat, keywords: List[str]) -> Dict[str, str]:
    comment_pattern = r'^\*'
    with open(file_path, 'r', encoding="utf-8", errors='ignore') as f:
        matched_lines: List[str] = [line for line in f.readlines()
                                    if not re.match(comment_pattern, line)]
        lines: List[List[str]] = [[key_value.strip().strip(";") for key_value
                                   in line.strip().split("=", 1)]
                                  for line in matched_lines]
        obs_info_lines: List[List[str]] = [line for line in lines if line[0] in vex_keywords()]
        return make_obs_list(obs_info_lines, file_stat,
                             make_keyword_dict(keywords))


def make_obs_list(obs_info_lines: List[List[str]],
                  file_stat: oper.FileStat,
                  keyword_dict: Dict[str, str]) -> Dict[str, str]:
    def convert_value(file_keyword: str, value: str) -> str:
        if (file_keyword == 'exper_nominal_start'
                or file_keyword == 'exper_nominal_stop'):
            value = time_string2time(value)
        elif file_keyword == 'ref $IF':
            band_pattern = r'^IF_([\w])+:'
            if re.match(band_pattern, value):
                value = re.search(band_pattern, value).group(1)
            else:
                value = 'unknown'
        return value

    obs_list: Dict[str, str] = {keyword_dict[keyword]: convert_value(keyword, value)
                                for keyword, value in obs_info_lines}
    return add_timestamp(add_names(obs_list), file_stat)


def add_names(obs_list: Dict[str, str]) -> Dict[str, str]:
    keys_read: KeysView[str] = obs_list.keys()

    if 'PI_name' in keys_read and 'contact_name' in keys_read:
        return obs_list
    if 'contact_name' in keys_read:
        obs_list['PI_name'] = obs_list['contact_name']
        return obs_list
    if 'PI_name' in keys_read:
        obs_list['contact_name'] = obs_list['PI_name']
        return obs_list
    obs_list['contact_name'] = 'unknown'
    obs_list['PI_name'] = obs_list['contact_name']
    return obs_list


def add_timestamp(obs_list: Dict[str, str], file_stat: oper.FileStat) -> Dict[str, str]:
    obs_list['timestamp'] = file_stat.st_mtime
    return obs_list
