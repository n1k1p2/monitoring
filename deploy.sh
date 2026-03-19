#!/bin/bash
set -e

echo "🚀 Starting Django Monitoring deploy..."

# 1. Update system packages
echo "Обновление системы..."
sudo apt-get update -y

# 2. Install Docker if not present
if ! command -v docker &> /dev/null
then
    echo "🐳 Docker не найден. Устанавливаю Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker успешно установлен."
else
    echo "🐳 Docker уже установлен."
fi

# 3. Ensure docker compose plugin is ready
if ! docker compose version &> /dev/null
then
    echo "❌ Плагин Docker Compose не найден. Установите его через 'sudo apt-get install docker-compose-plugin'"
    exit 1
fi

# 4. Spin up the project
echo "📦 Собираю и запускаю контейнеры..."
sudo docker compose up --build -d

echo ""
echo "🎉 Готово! Проект успешно запущен."
echo "🌐 Админка будет доступна по адресу: http://<IP_ТВОЕГО_СЕРВЕРА>:8000/admin"
echo "Чтобы посмотреть логи воркеров, используй: sudo docker compose logs -f celery_worker"
