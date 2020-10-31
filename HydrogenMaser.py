import datetime as d
from .VERAStatus import HydrogenMaserServer as s
import my_utilities.utilities as u


def status_parameters():
    return [
        {'label': 'total_days_from_19000101',
         'accuracy': 0, 'unit': 'days'},
        {'label': 'time', 'accuracy': 0, 'unit': ''},
        {'label': 'temperature_cavity',
         'accuracy': 0.001, 'unit': 'Cdeg'},
        {'label': 'temperature_shield1_main',
         'accuracy': 0.001, 'unit': 'Cdeg'},
        {'label': 'temperature_shield2_lower',
         'accuracy': 0.001, 'unit': 'Cdeg'},
        {'label': 'temperature_shield3_upper',
         'accuracy': 0.001, 'unit': 'Cdeg'},
        {'label': 'temperature_shield3_main',
         'accuracy': 0.001, 'unit': 'Cdeg'},
        {'label': 'temperature_shield3_lower',
         'accuracy': 0.001, 'unit': 'Cdeg'},
        {'label': 'temperature_electronics',
         'accuracy': 0.001, 'unit': 'Cdeg'},
        {'label': 'temperature_room',
         'accuracy': 0.001, 'unit': 'Cdeg'},
        {'label': 'H_pressure_source_kPa',
         'accuracy': 0.001, 'unit': 'kPa'},
        {'label': 'H_pressure_cell',
         'accuracy': 0.01, 'unit': 'Pa', 'daily_report_index': 2},
        {'label': 'dissociate_intensity',
         'accuracy': 1, 'unit': '', 'daily_report_index': 1},
        {'label': 'OCXO_control_voltage',
         'accuracy': 0.01, 'unit': 'V', 'daily_report_index': 5},
        {'label': 'maser_RX_level',
         'accuracy': 0.1, 'unit': 'dBm', 'daily_report_index': 4},
        {'label': 'cavity_IF_level',
         'accuracy': 0.001, 'unit': 'V'},
        {'label': 'cavity_automatic_tube_error_voltage',
         'accuracy': 0.001, 'unit': 'V'},
        {'label': 'varicap_voltage',
         'accuracy': 0.01, 'unit': 'V', 'daily_report_index': 3},
        {'label': 'ion_pump_current',
         'accuracy': 0.001, 'unit': 'mA', 'daily_report_index': 0},
        {'label': 'ion_pump_voltage',
         'accuracy': 0.001, 'unit': 'kV'},
        {'label': 'dissociation_drive_current',
         'accuracy': 0.0001, 'unit': 'A'},
        {'label': 'battery_voltage',
         'accuracy': 0.001, 'unit': 'V'},
        {'label': 'battery_current',
         'accuracy': 0.0001, 'unit': 'A', 'daily_report_index': 6},
        {'label': 'battery_charge_voltage',
         'accuracy': 0.001, 'unit': 'V'},
        {'label': 'power_supply_voltage+24',
         'accuracy': 0.001, 'unit': 'V'},
        {'label': 'power_supply_voltage+12',
         'accuracy': 0.001, 'unit': 'V'},
        {'label': 'power_supply_voltage-12',
         'accuracy': 0.001, 'unit': 'V'},
        {'label': 'power_analog_supply_voltage+5',
         'accuracy': 0.001, 'unit': 'V'},
        {'label': 'power_digital_supply_voltage+5',
         'accuracy': 0.001, 'unit': 'V'},
        {'label': 'power_supply_voltage+3.3',
         'accuracy': 0.001, 'unit': 'V'},
        {'label': 'reserve',
         'accuracy': 0.001, 'unit': 'Cdeg'},
    ]


def report_parameters():
    report_params = \
        filter(lambda x: x.get('daily_report_index') is not None,
               status_parameters())
    return sorted(report_params, key=lambda x: x['daily_report_index'])


def get(date_from, date_until=u.in_JST(d.datetime.now())):
    return s.get_status(date_from, date_until)


if __name__ == '__main__':

    status = get(u.in_JST(d.datetime.combine(d.date.today(), d.time())))
    for param in report_parameters():
        print(param['label'] + ':',
              status[-1][param['label']], param['unit'])
