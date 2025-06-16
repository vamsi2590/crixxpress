FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install gunicorn && pip install -r requirements.txt


COPY . .

# Collect static files at build time
RUN python manage.py collectstatic --no-input

EXPOSE 8080

CMD ["gunicorn", "CricSphere.wsgi:application", "--bind", "0.0.0.0:8080"]
