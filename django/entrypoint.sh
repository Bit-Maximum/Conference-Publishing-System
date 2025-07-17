#!/bin/bash

echo "Make database migrations"
python manage.py makemigrations --noinput

echo "Apply database migrations"
python manage.py migrate --noinput

#echo "Collect statics"
#python manage.py collectstatic --noinput

exec "$@"