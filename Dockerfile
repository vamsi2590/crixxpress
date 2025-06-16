FROM python:3.11-slim

# Set environment variables (PROPERLY escaped)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application
COPY . .

# Single command to run everything (proper quoting)
CMD sh -c "python manage.py migrate && python manage.py collectstatic --no-input && gunicorn CricSphere.wsgi:application --bind 0.0.0.0:8080"
