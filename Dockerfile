FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["sh", "-c", "python bot.py & exec gunicorn --workers ${WORKERS:-2} --bind 0.0.0.0:${PORT:-8000} wsgi:app"]
