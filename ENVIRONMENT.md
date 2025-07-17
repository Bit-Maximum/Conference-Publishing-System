# 📄 Environment Variables for Running the Conference Publishing System

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/Bit-Maximum/Conference-Publishing-System/blob/main/ENVIRONMENT.md)
[![ru](https://img.shields.io/badge/lang-ru-blue.svg)](https://github.com/Bit-Maximum/Conference-Publishing-System/blob/main/translation/ENVIRONMENT.ru.md)

The `.env` file contains configuration parameters required for setting up and running the project. Below is an explanation of both **mandatory** and **optional** environment variables.

---

## ✅ Mandatory Variables (`MANDATORY`)

### 🔐 Security

| Variable        | Description                                                                                    |
| --------------- | ---------------------------------------------------------------------------------------------- |
| `SECRET_KEY`    | Django secret key used for signing cookies and other operations. Must be unique and secure.    |
| `ALLOWED_HOSTS` | Comma-separated list of domains/IPs allowed to access the site. Example: `localhost,127.0.0.1` |

---

### 🛢 Database

| Variable      | Description                                      |
| ------------- | ------------------------------------------------ |
| `DB_ENGINE`   | Database engine. Default: `postgresql_psycopg2`. |
| `DB_NAME`     | Name of the database.                            |
| `DB_USER`     | Database username.                               |
| `DB_PASSWORD` | Database user password.                          |
| `DB_HOST`     | Database host address. In Docker, usually `db`.  |
| `DB_PORT`     | Database connection port. Default: `5432`.       |

---

### ✉️ Email

| Variable                   | Description                                                     |
| -------------------------- | --------------------------------------------------------------- |
| `EMAIL_HOST`               | SMTP server for sending emails.                                 |
| `EMAIL_HOST_PORT`          | SMTP port (typically `587` for TLS).                            |
| `EMAIL_USE_TLS`            | Whether to use TLS (`True` / `False`).                          |
| `DEFAULT_FROM_EMAIL`       | Email address used as the sender for system messages.           |
| `EMAIL_HOST_USER`          | SMTP username (often the same as sender email).                 |
| `EMAIL_HOST_PASSWORD`      | Password or app-specific token for SMTP user.                   |
| `MASS_FROM_EMAIL`          | Email used for mass mailings (e.g. conference program).         |
| `MASS_EMAIL_HOST_USER`     | SMTP username for bulk email.                                   |
| `MASS_EMAIL_HOST_PASSWORD` | Password or token for bulk email SMTP.                          |
| `EMAIL_PAGE_DOMAIN`        | Base URL shown in email messages (e.g. for confirmation links). |
| `EMAIL_MAIL_SUBJECT`       | Default subject line used in platform-generated emails.         |

---

### ☁️ Cloud Storage

| Variable       | Description                                                      |
| -------------- | ---------------------------------------------------------------- |
| `YADISK_TOKEN` | OAuth token for accessing Yandex Disk. Used for document upload. |

---

### 📋 Logging

| Variable           | Description                                            |
| ------------------ | ------------------------------------------------------ |
| `LOGGING_TO_EMAIL` | Admin email address to receive critical error reports. |

---

## ⚙️ Optional Variables (`OPTIONAL`)

| Variable               | Description                                                                                     |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| `DEBUG`                | Enables debug mode (`True` / `False`). Must be `False` in production.                           |
| `SITE_NAME`            | Project name shown on the website and in email templates.                                       |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for CSRF protection. Used when deploying on custom domains.                     |
| `CLOUD_BASE_URL`       | Custom URL of the document auto-formatting microservice (if externalized). Must end with a `/`. |
| `CELERY_BROKER`        | Celery task broker URL. Usually Redis (e.g. `redis://redis:6379/0`).                            |

---

## 📌 Example `.env` File

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