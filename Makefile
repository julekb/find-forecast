up:
	docker-compose up -d

down:
	docker-compose down

rebuild:
	docker-compose up --build --force-recreate --no-deps -d

bash:
	docker exec -it find-forecast-find-forecast-1 bash

test:
	bash
	pytest