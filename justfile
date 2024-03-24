CONTAINER := "find-forecast-find-forecast-1"
SERVICE := "find-forecast"
TEST_DIR := "tests/."

up:
	docker-compose up -d

stop:
    docker-compose stop

down:
	docker-compose down -v

build:
	docker-compose build

rebuild:
	docker-compose up --build --force-recreate --no-deps -d

ps:
    docker-compose ps

bash: up
	docker exec -it {{CONTAINER}} bash

test dir=TEST_DIR:
	docker-compose run {{SERVICE}} pytest {{dir}}
