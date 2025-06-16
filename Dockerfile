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

# 4. (Optional) Run migrations at build time (if really needed)
# RUN python manage.py migrate --no-input
# RUN python manage.py collectstatic --no-input

# 5. Run Gunicorn
CMD ["gunicorn", "Morax.wsgi:application", "--bind", "0.0.0.0:8080"]
