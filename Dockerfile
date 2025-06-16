FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
CMD ["sh", "-c", "python manage.py migrate && gunicorn CricSphere.wsgi:application --bind 0.0.0.0:8080"]
