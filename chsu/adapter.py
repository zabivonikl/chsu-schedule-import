from datetime import datetime
from itertools import groupby


def get_google_calendar_events(json, user_type):
    print("Преобразование в мероприятия Google Calendar...")
    events = []
    grouped_json = groupby(json, key=lambda e: e['dateEvent'])
    for date, school_day in grouped_json:
        grouped_school_day = groupby(list(school_day), key=lambda e: _get_discipline_string(e))
        for discipline_title, couples in grouped_school_day:
            couples = list(couples)
            events.append({
                'summary': discipline_title,
                'location': _get_location(couples[0]),
                'description': _get_description(couples[0], user_type),
                'start': {
                    'dateTime': str(_get_start_date_time(couples[0]).isoformat()),
                    'timeZone': 'Europe/Moscow',
                },
                'end': {
                    'dateTime': str(_get_end_date_time(couples[-1]).isoformat()),
                    'timeZone': 'Europe/Moscow',
                },
                'reminders': {
                    'useDefault': True,
                },
            })

    return events


def _get_discipline_string(couple):
    if couple["abbrlessontype"]:
        couple["abbrlessontype"] += "., "
    return f'''{couple["abbrlessontype"] or ''}{couple['discipline']['title']}'''


def _get_description(couple, user_type) -> str:
    def _get_professors_names():
        response = ""
        for professor in couple['lecturers']:
            response += f"{professor['fio']}, "
        return f"Преподаватель(-и): {response[:-2]}"

    def _get_groups_names():
        response = ""
        for group in couple['groups']:
            response += f"{group['title']}, "
        return f"Группа(-ы): {response[:-2]}"

    return _get_professors_names() if user_type == 'student' else _get_groups_names()


def _get_location(couple) -> str:
    def get_address():
        return f"{couple['build']['title']}, аудитория {couple['auditory']['title']}"

    return "Онлайн\n" if couple['online'] == 1 else get_address()


def _get_start_date_time(couple):
    return datetime.strptime(f"{couple['dateEvent']} {couple['startTime']}", "%d.%m.%Y %H:%M")


def _get_end_date_time(couple):
    return datetime.strptime(f"{couple['dateEvent']} {couple['endTime']}", "%d.%m.%Y %H:%M")
