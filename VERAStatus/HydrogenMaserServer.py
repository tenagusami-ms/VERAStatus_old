import os
import glob
import datetime as d
# import HydrogenMaser as H
from my_settings.settings import H_maser_setting as setting

from VERAStatus.Utility import in_jst, columnize, round_float, coefficient_Torr2Pa


def data_file_paths():
    directories = glob.glob(setting()['data_root'] + '/*')
    return sum([glob.glob(directory + '/hm_only_mdata*.txt')
                for directory in directories], [])


def file_name2_date_from(file_name):
    date = in_jst(
        d.datetime.strptime('20' + file_name[13:23] + '00',
                            '%Y%m%d%H%M%S'))
    date += d.timedelta(seconds=int(file_name[23]) * 10)
    return date


def data_file_info():
    paths = data_file_paths()
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
    cols = columnize(line, '\t')
    parameters = H.status_parameters()
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
                float(col)*0.001 * coefficient_Torr2Pa(), param['accuracy'])
            continue
        status[param['label']] = round_float(col, param['accuracy'])
    return status


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


def get_status(date_from, date_until, step_interval=10):
    file_paths = data_files(data_file_info(), date_from, date_until)
    return sum([read(path, date_from, date_until, step_interval)
                for path in file_paths], [])
