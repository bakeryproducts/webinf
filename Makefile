.PHONY: all up attach stop restart
CONFIG=config/config.env
include ${CONFIG}

all: up
up:
	docker-compose -f ./docker-compose.yml --env-file ${CONFIG} up --build --detach
stop:
	docker-compose down
restart: stop up
