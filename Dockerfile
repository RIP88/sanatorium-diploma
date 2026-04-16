# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Устанавливаем системные зависимости для работы с базой данных и сборки пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя app для безопасности
RUN groupadd --gid 2000 app && useradd --uid 2000 --gid 2000 -m -d /app app

# Переходим в рабочую директорию
WORKDIR /app

# Копируем файлы проекта с правильными правами
COPY --chown=app:app . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Переключаемся на пользователя app
USER app

# Открываем порт 8000
EXPOSE 8000

# Команда запуска Gunicorn
# Важно: указываем правильный путь к wsgi.py (config.wsgi:application)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "config.wsgi:application"]