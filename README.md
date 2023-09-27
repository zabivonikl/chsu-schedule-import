# Скрипт для импорта расписания Череповецкого Государственного Университета в Google Calendar

## Настройка
Перед запуском необходимо установить необходимые зависимости с помощью команды:

```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

После установки зависимостей нужно создать файл `credentials.json`, в котором будут лежать 
данные Google-приложения. Содержимое файла можно получить, воспользовавшись
[инструкцией](https://developers.google.com/calendar/api/quickstart/python#set_up_your_environment).

Приложение использует OAuth 2.0 авторизацию со следующими scopes:
* `.../auth/calendar`;
* `.../auth/calendar.readonly`.

## Запуск 
Скрипт запускается командой `python main.py`. 

При первом запуске потребуется войти в свой Google-аккаунт. Токен, полученный при входе, 
сохраняется в файл `token.json`.

## Исключение при запуске
Если при запуске возникает необработанное исключение, то проверьте `credentials.json` на актуальность
или удалите `token.json`.
