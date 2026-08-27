FROM python:3.11-slim

WORKDIR /app

# Щоб Python бачив імпорти з усіх папок проєкту
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 --retries 10 -r requirements.txt

COPY . .

# Шлях до вашого bot.py всередині папки tesing
CMD ["python", "tesing/bot.py"]