import dataclasses
import os
import pathlib as p
import datetime as d
from typing import Dict, Any

from .Utility import in_jst, round_float, Torr2PaCoefficient


@dataclasses.dataclass
class MaserSettings:
    data_prefix_directory: p.Path


def read_settings(settings_dict: Dict[str, Any]) -> MaserSettings:
    return MaserSettings(
        p.Path(settings_dict[os.name]["os_root"]) / settings_dict["data_prefix_directory"])


def status_parameters():
    return [
        {'label': 'total_days_from_19000101',
         'accuracy': 0, 'unit': 'days'},
        {'label': 'time', 'accuracy': 0, 'unit': ''},
        {'label': 'temperature_cavity',
         'accuracy': -3, 'unit': 'Cdeg'},
        {'label': 'temperature_shield1_main',
         'accuracy': -3, 'unit': 'Cdeg'},
        {'label': 'temperature_shield2_lower',
         'accuracy': -3, 'unit': 'Cdeg'},
        {'label': 'temperature_shield3_upper',
         'accuracy': -3, 'unit': 'Cdeg'},
        {'label': 'temperature_shield3_main',
         'accuracy': -3, 'unit': 'Cdeg'},
        {'label': 'temperature_shield3_lower',
         'accuracy': -3, 'unit': 'Cdeg'},
        {'label': 'temperature_electronics',
         'accuracy': -3, 'unit': 'Cdeg'},
        {'label': 'temperature_room',
         'accuracy': -3, 'unit': 'Cdeg'},
        {'label': 'H_pressure_source_kPa',
         'accuracy': -3, 'unit': 'kPa'},
        {'label': 'H_pressure_cell',
         'accuracy': -2, 'unit': 'Pa', 'daily_report_index': 2},
        {'label': 'dissociate_intensity',
         'accuracy': 0, 'unit': '', 'daily_report_index': 1},
        {'label': 'OCXO_control_voltage',
         'accuracy': -2, 'unit': 'V', 'daily_report_index': 5},
        {'label': 'maser_RX_level',
         'accuracy': -1, 'unit': 'dBm', 'daily_report_index': 4},
        {'label': 'cavity_IF_level',
         'accuracy': -3, 'unit': 'V'},
        {'label': 'cavity_automatic_tube_error_voltage',
         'accuracy': -3, 'unit': 'V'},
        {'label': 'varicap_voltage',
         'accuracy': -2, 'unit': 'V', 'daily_report_index': 3},
        {'label': 'ion_pump_current',
         'accuracy': -3, 'unit': 'mA', 'daily_report_index': 0},
        {'label': 'ion_pump_voltage',
         'accuracy': -3, 'unit': 'kV'},
        {'label': 'dissociation_drive_current',
         'accuracy': -4, 'unit': 'A'},
        {'label': 'battery_voltage',
         'accuracy': -3, 'unit': 'V'},
        {'label': 'battery_current',
         'accuracy': -4, 'unit': 'A', 'daily_report_index': 6},
        {'label': 'battery_charge_voltage',
         'accuracy': -3, 'unit': 'V'},
        {'label': 'power_supply_voltage+24',
         'accuracy': -3, 'unit': 'V'},
        {'label': 'power_supply_voltage+12',
         'accuracy': -3, 'unit': 'V'},
        {'label': 'power_supply_voltage-12',
         'accuracy': -3, 'unit': 'V'},
        {'label': 'power_analog_supply_voltage+5',
         'accuracy': -3, 'unit': 'V'},
        {'label': 'power_digital_supply_voltage+5',
         'accuracy': -3, 'unit': 'V'},
        {'label': 'power_supply_voltage+3.3',
         'accuracy': -3, 'unit': 'V'},
        {'label': 'reserve',
         'accuracy': -3, 'unit': 'Cdeg'},
    ]


def data_file_paths(settings: MaserSettings):
    directories = settings.data_prefix_directory.glob(r"*")
    return sum([directory.glob(r"hm_only_mdata*.txt")
                for directory in directories], [])


def file_name2_date_from(file_name):
    date = in_jst(
        d.datetime.strptime('20' + file_name[13:23] + '00',
                            '%Y%m%d%H%M%S'))
    date += d.timedelta(seconds=int(file_name[23]) * 10)
    return date


def data_file_info(settings: MaserSettings):
    paths = data_file_paths(settings)
    dates = [file_name2_date_from(os.path.basename(file_path))
             for file_path in paths]
    paths_dates = [{'path': path, 'date_from': date_from}
                   for path, date_from in zip(paths, dates)]
    sorted_path_dates = sorted(paths_dates, key=lambda x: x['date_from'])
    for index, file_info in enumerate(sorted_path_dates[:-1]):
        file_info['date_until'] = sorted_path_dates[index + 1]['date_from']
    sorted_path_dates[-1]['date_until'] = \
        in_jst(d.datetime.now())
    return sorted_path_dates


def data_files(file_info_list, date_from, date_until):
    return [file_info['path'] for file_info in file_info_list
            if date_from <= file_info['date_until']
            and date_until > file_info['date_from']]


def line2status(line):
    cols = [value_string.strip() for value_string in line.strip().split("\t")]
    parameters = status_parameters()
    status = {}
    for param, col in zip(parameters, cols):
        if param['label'] == 'time':
            status[param['label']] = in_jst(
                d.datetime.strptime(
                    '20' + col[0] + col[2:11] + '00',
                    '%Y%m%d%H%M%S'))
            status[param['label']] += d.timedelta(
                seconds=int(col[11]) * 10)
            continue
        if param['label'] == 'H_pressure_cell':
            status[param['label']] = round_float(
                float(col) * 0.001 * Torr2PaCoefficient, param['accuracy'])
            continue
        status[param['label']] = round_float(col, param['accuracy'])
    return status


def get(settings: MaserSettings, date_from, date_until=in_jst(d.datetime.now())):
    return get_status(settings, date_from, date_until)


def read(path, date_from, date_until, step_interval):
    with open(path, 'r') as f:
        lines = f.readlines()
        status_list = []
        for index, line in enumerate(lines):
            if index % step_interval == 0:
                status = line2status(line)
                if date_from <= status['time'] < date_until:
                    status_list.append(status)
        return status_list


def get_status(settings: MaserSettings, date_from, date_until, step_interval=10):
    file_paths = data_files(data_file_info(settings), date_from, date_until)
    return sum([read(path, date_from, date_until, step_interval)
                for path in file_paths], [])


def report_parameters():
    report_params = \
        filter(lambda x: x.secz_1day('daily_report_index') is not None,
               status_parameters())
    return sorted(report_params, key=lambda x: x['daily_report_index'])
