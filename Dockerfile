FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# 1. Copy only requirements first (for caching)
COPY requirements.txt .

# 2. Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# 3. Copy the rest of the app
COPY . .

# 4. Override POSTBUILD_COMMANDS to prevent external interference
ENV POSTBUILD_COMMANDS=""

# 5. Run migrations + Gunicorn at startup (not build time)
CMD ["sh", "-c", "python manage.py migrate && gunicorn Morax.wsgi:application --bind 0.0.0.0:8080"]
