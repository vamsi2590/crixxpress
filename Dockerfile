FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y gcc \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --no-input && gunicorn CricSphere.wsgi:application --bind 0.0.0.0:8080"]
