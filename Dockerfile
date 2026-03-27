FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV CELERY_BROKER_URL=redis://host.docker.internal:6379/0

CMD ["celery","-A","tasks","worker","--loglevel=INFO"]
