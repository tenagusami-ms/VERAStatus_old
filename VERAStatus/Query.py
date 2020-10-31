import asyncio
import vlbi.schedule.schedule as sched
import vlbi.utility as u
import vlbi.secZ.secZ as secZ


def get_status(doy_string):
    today = u.doy_string2datetime(doy_string)
    if today > u.get_now():
        raise RuntimeError('specified date ' + doy_string + ' is in future.')
    status_info = get_status_today(today)
    return {
        'observation_info':
            sched.info_list2lines_list(status_info['observation_info']),
        'secZ_info':
            secZ.info_list2lines_list(status_info['secZ_info']),
    }


def get_status_today(today):
    task1 = asyncio.ensure_future(sched.get_observations(today, today))
    task2 = asyncio.ensure_future(secZ.get(today))
    obs_info_list, secZ_info_list = u.async_execution([task1, task2])
    return {'observation_info': obs_info_list,
            'secZ_info': secZ_info_list}


def get_status_today_synchronous(today):
    status = {'observation_info': sched.get_observations(today, today),
              'secZ_info': secZ.get(today)}
    # print(status)
    return status


def get_status_synchronous(date_from, date_until):
    status = {'observation_info': sched.get_observations(date_from, date_until),
              'secZ_info': secZ.get(date_from)}
    # print(status)
    return status
