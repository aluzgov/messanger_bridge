restart:
	docker-compose build app
	docker-compose down -t 1
	docker-compose up -d --build
