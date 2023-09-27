import requests

from chsu.adapter import get_google_calendar_events


class Chsu:
    def __init__(self):
        self._base_url = "http://api.chsu.ru/api"
        self._headers = {
            "Content-Type": "application/json"
        }
        self._login_and_password = {
            "username": "mobil",
            "password": "ds3m#2nn"
        }
        self._id_by_professors = None
        self._id_by_groups = None
        response = requests.post(
            f"http://api.chsu.ru/api/auth/signin",
            headers=self._headers,
            json=self._login_and_password
        ).json()
        if 'data' in response:
            self._headers["Authorization"] = f'''Bearer {response['data']}'''

    async def get_user_type(self, name: str):
        if name in (await self._get_id_by_professors_list()).keys():
            return "professor"
        elif name in (await self._get_id_by_groups_list()).keys():
            return "student"
        else:
            return None

    async def _get_id_by_professors_list(self):
        if self._id_by_professors is None:
            await self._refresh_professors_list()
        return self._id_by_professors

    async def _refresh_professors_list(self):
        teachers = requests.get(self._base_url + "/teacher/v1", headers=self._headers).json()
        self._id_by_professors = {}
        for teacher in teachers:
            self._id_by_professors[teacher["fio"]] = teacher['id']

    async def _get_id_by_groups_list(self):
        if self._id_by_groups is None:
            await self._refresh_groups_list()
        return self._id_by_groups

    async def _refresh_groups_list(self):
        groups = requests.get(self._base_url + "/group/v1", headers=self._headers).json()
        self._id_by_groups = {}
        for group in groups:
            self._id_by_groups[group["title"]] = group['id']

    async def get_google_calendar_event(self, name: str, start_date: str, last_date: str = None):
        return get_google_calendar_events(
            await self._get_schedule_json(name, start_date, last_date),
            await self.get_user_type(name)
        )

    async def _get_schedule_json(self, name: str, start_date: str, last_date: str = None):
        print("Получение расписания...")
        response = requests.get(
            f"{self._base_url}/timetable/v1/"
            f"from/{start_date}/"
            f"to/{last_date or start_date}/"
            f"{(await self.get_user_type(name)).replace('student', 'groupId').replace('professor', 'lecturerId')}/"
            f"{await self._get_chsu_id(name)}/",
            headers=self._headers
        ).json()
        if 'description' in response:
            raise ConnectionError(f"{response['code']}: {response['description']}")
        return response

    async def _get_chsu_id(self, name: str):
        return {
            **(await self._get_id_by_groups_list()),
            **(await self._get_id_by_professors_list())
        }[name]
