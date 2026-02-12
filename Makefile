.PHONY: build up down restart logs shell clean rebuild

# Сборка образа
build:
	docker-compose build

# Запуск контейнера
up:
	docker-compose up -d

# Остановка контейнера
down:
	docker-compose down

# Перезапуск контейнера
restart:
	docker-compose restart

# Просмотр логов
logs:
	docker-compose logs -f

# Просмотр последних 100 строк логов
logs-tail:
	docker-compose logs -f --tail=100

# Вход в контейнер
shell:
	docker-compose exec studyshorts-bot /bin/bash

# Очистка (остановка + удаление volumes)
clean:
	docker-compose down -v
	docker system prune -f

# Пересборка и запуск
rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# Статус контейнера
status:
	docker-compose ps

# Бэкап базы данных
backup:
	mkdir -p backups
	docker cp studyshorts-bot:/app/data/studyshorts.db ./backups/studyshorts_$(shell date +%Y%m%d_%H%M%S).db

# Восстановление базы данных (использование: make restore FILE=backups/studyshorts_xxx.db)
restore:
	docker cp $(FILE) studyshorts-bot:/app/data/studyshorts.db
	docker-compose restart

# Продакшен сборка
prod-up:
	docker-compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker-compose -f docker-compose.prod.yml down