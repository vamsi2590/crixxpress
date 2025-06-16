FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8080

# Use entrypoint to run collectstatic and migrate at container startup
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --no-input && gunicorn CricSphere.wsgi:application --bind 0.0.0.0:8080"]
