FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=fengyun.settings

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput && python manage.py ensure_admin

EXPOSE 8000

CMD gunicorn fengyun.wsgi --bind 0.0.0.0:8000 --workers 2