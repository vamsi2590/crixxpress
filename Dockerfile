FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# No CMD needed here (Kuern will use Deploy Config)

# At the very end of your Dockerfile
RUN echo "#!/bin/sh\npython manage.py migrate\npython manage.py collectstatic --no-input\nexec gunicorn CricSphere.wsgi:application --bind 0.0.0.0:8080" > /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
