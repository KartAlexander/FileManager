#!/bin/bash

# Убиваем процесс, занимающий порт 8000
PORT=8000
PID=$(lsof -ti :$PORT)

if [ ! -z "$PID" ]; then
    echo "Убиваем процесс, занимающий порт $PORT (PID: $PID)..."
    kill -9 $PID
fi

python manage.py runserver 0.0.0.0:$PORT &

# Запускаем фронтенд
cd frontend || { echo "Ошибка: папка frontend не найдена"; exit 1; }

npm run dev
