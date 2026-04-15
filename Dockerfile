FROM python:3.10-slim

# Установка системных зависимостей
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя app
RUN groupadd --gid 2000 app && useradd --uid 2000 --gid 2000 -m -d /app app

WORKDIR /app

# Копирование файлов с правильными правами
COPY --chown=app:app . .

# Установка зависимостей Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Переключение на пользователя app
USER app

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]