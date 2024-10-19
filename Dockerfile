FROM python:3.11.3-slim-bullseye AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD [ "sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8000" ]
