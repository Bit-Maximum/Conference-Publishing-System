# 📄 Переменные окружения для запуска Conference Publishing System

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/Bit-Maximum/Conference-Publishing-System/blob/main/ENVIRONMENT.md)
[![ru](https://img.shields.io/badge/lang-ru-blue.svg)](https://github.com/Bit-Maximum/Conference-Publishing-System/blob/main/translation/ENVIRONMENT.ru.md)

Файл `.env` содержит параметры, необходимые для настройки и запуска проекта. Ниже представлены пояснения к обязательным и опциональным переменным окружения.

---

## ✅ Обязательные переменные (`MANDATORY`)

### 🔐 Безопасность

| Переменная         | Описание |
|--------------------|----------|
| `SECRET_KEY`       | Секретный ключ Django для подписи cookies и других операций. Должен быть уникальным и надёжным. |
| `ALLOWED_HOSTS`    | Список доменов/IP, с которых разрешён доступ к сайту (через запятую). Например: `localhost,127.0.0.1` |

---

### 🛢 База данных

| Переменная       | Описание |
|------------------|----------|
| `DB_ENGINE`      | Движок базы данных. По умолчанию: `postgresql_psycopg2`. |
| `DB_NAME`        | Название базы данных. |
| `DB_USER`        | Имя пользователя базы данных. |
| `DB_PASSWORD`    | Пароль пользователя БД. |
| `DB_HOST`        | Адрес сервера базы данных. В Docker-среде обычно `db`. |
| `DB_PORT`        | Порт для подключения к БД. По умолчанию: `5432`. |

---

### ✉️ Почта

| Переменная              | Описание |
|-------------------------|----------|
| `EMAIL_HOST`            | SMTP-сервер для отправки писем. |
| `EMAIL_HOST_PORT`       | Порт SMTP-сервера (обычно `587` для TLS). |
| `EMAIL_USE_TLS`         | Использовать TLS (`True`/`False`). |
| `DEFAULT_FROM_EMAIL`    | Email-адрес, от имени которого отправляются системные письма. |
| `EMAIL_HOST_USER`       | SMTP-пользователь (часто совпадает с адресом отправителя). |
| `EMAIL_HOST_PASSWORD`   | Пароль или app-token для SMTP-пользователя. |
| `MASS_FROM_EMAIL`       | Email для массовых рассылок (например, программа конференции). |
| `MASS_EMAIL_HOST_USER`  | SMTP-пользователь для массовых рассылок. |
| `MASS_EMAIL_HOST_PASSWORD` | Пароль или токен для массовой рассылки. |
| `EMAIL_PAGE_DOMAIN`     | URL сайта, отображаемый в теле письма (например, для ссылок подтверждения). |
| `EMAIL_MAIL_SUBJECT`    | Тема, используемая по умолчанию для писем от платформы. |

---

### ☁️ Облачное хранилище

| Переменная     | Описание |
|----------------|----------|
| `YADISK_TOKEN` | OAuth-токен для доступа к Яндекс.Диску. Используется для загрузки документов. |

---

### 📋 Логирование

| Переменная        | Описание |
|-------------------|----------|
| `LOGGING_TO_EMAIL`| Email-адрес администратора, на который будут отправляться критические ошибки. |

---

## ⚙️ Опциональные переменные (`OPTIONAL`)

| Переменная          | Описание |
|---------------------|----------|
| `DEBUG`             | Включение режима отладки (`True` / `False`). В продакшене должен быть `False`. |
| `SITE_NAME`         | Название проекта, отображаемое на сайте и в шаблонах писем. |
| `CSRF_TRUSTED_ORIGINS` | Разрешённые источники для защиты от CSRF. Используется при деплое на собственные домены. |
| `CLOUD_BASE_URL`    | Кастомный адрес микросервиса автообработки документов (если вынесен отдельно). Должен заканчиваться на `/`. |
| `CELERY_BROKER`     | Адрес брокера задач Celery. Обычно используется Redis (например, `redis://redis:6379/0`). |

---

## 📌 Пример `.env`

```env
SECRET_KEY=my-super-secret
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=postgresql_psycopg2
DB_NAME=dockerdjango
DB_USER=dbuser
DB_PASSWORD=dockerdjango
DB_HOST=db
DB_PORT=5432

EMAIL_HOST=smtp.yandex.ru
EMAIL_HOST_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=temp@mail.com
EMAIL_HOST_USER=temp@mail.com
EMAIL_HOST_PASSWORD=your-email-password
MASS_FROM_EMAIL=mass@mail.com
MASS_EMAIL_HOST_USER=mass@mail.com
MASS_EMAIL_HOST_PASSWORD=your-email-password
EMAIL_PAGE_DOMAIN=http://127.0.0.1:8000
EMAIL_MAIL_SUBJECT='Conference Pablishing System'

YADISK_TOKEN=your-yandex-disk-token
LOGGING_TO_EMAIL=admin@example.com

DEBUG=True
SITE_NAME='Conference Pablishing System'
CSRF_TRUSTED_ORIGINS=http://*.localhost,http://*.127.0.0.1
CLOUD_BASE_URL=http://127.0.0.1:8000/
CELERY_BROKER=redis://redis:6379/0
```