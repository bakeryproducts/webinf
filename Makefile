.PHONY: all up down restart
CONFIG=config/config.env
include ${CONFIG}

all: up
up:
	docker-compose -f ./docker-compose.yml --env-file ${CONFIG} up --build --detach
down:
	docker-compose down
restart: down up
