FROM python:3.12-slim-bookworm

WORKDIR /usr/src/app

# prevent python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# prevent python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

USER django-user

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]