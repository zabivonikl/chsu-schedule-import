from __future__ import print_function

import asyncio
import os.path
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from chsu.client import Chsu

SCOPES = ['https://www.googleapis.com/auth/calendar']

event_loop = asyncio.get_event_loop()
chsu_client = Chsu()


def _get_calendar_service():
    print("Создание Google-сервиса...")
    credentials = None
    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())

    return build('calendar', 'v3', credentials=credentials)


async def _get_group_calendars(service):
    print("Получение списка календарей-расписаний...")
    page_token = None
    group_names = []
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if str(calendar_list_entry['summary']).find("ЧГУ: ") != 0:
                continue
            calendar_name = calendar_list_entry['summary'][5:]
            chsu_type = await chsu_client.get_user_type(calendar_name)
            if chsu_type is not None:
                group_names.append((calendar_list_entry['id'], calendar_name))
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return group_names


async def _clear_calendar(service, calendar_id, from_date, to_date):
    print("Удаление старых мероприятий...")
    page_token = None
    while True:
        events = service.events().list(
            calendarId=calendar_id,
            pageToken=page_token,
            timeMin=str((datetime.strptime(from_date, "%d.%m.%Y") - timedelta(days=1)).isoformat()) + "Z",
            timeMax=str((datetime.strptime(to_date, "%d.%m.%Y") + timedelta(days=1)).isoformat()) + "Z"
        ).execute()
        for event in events['items']:
            service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
        page_token = events.get('nextPageToken')
        if not page_token:
            break


async def create_new():
    try:
        service = _get_calendar_service()

        member_name = input("Введите название группы/ФИО преподавателя: ")
        if await chsu_client.get_user_type(member_name) is None:
            print("Группа/преподаватель не найдены")
            return

        existing_calendars = await _get_group_calendars(service)
        calendar_names = map(lambda x: x[1], existing_calendars)
        selected_calendar = None

        if member_name in calendar_names:
            use_existed_calendar = int(input("Найден существующий календарь. Использовать его? (1 - Да, 0 - Нет) "))
            if use_existed_calendar == 1:
                selected_calendar = list(filter(lambda x: x[1] == member_name, existing_calendars))[0]

        start_date = input("Введите начальную дату в формате '01.01.2023': ")
        end_date = input("Введите конечную дату в формате '01.01.2023': ")
        calendar_events = await chsu_client.get_google_calendar_event(member_name, start_date, end_date)

        if selected_calendar is not None:
            await _clear_calendar(service, selected_calendar[0], start_date, end_date)
            calendar = service.calendarList().get(calendarId=selected_calendar[0]).execute()
        else:
            calendar_list_entry = {
                'summary': f"ЧГУ: {member_name}"
            }
            calendar = service.calendars().insert(body=calendar_list_entry).execute()

        print("Добавление мероприятий...")
        for event in calendar_events:
            service.events().insert(calendarId=calendar['id'], body=event).execute()
    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    event_loop.run_until_complete(create_new())
