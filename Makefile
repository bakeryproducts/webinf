.PHONY: all up attach stop
CONFIG=config/config.env
include ${CONFIG}                                                                                    

all: up attach
up:
	docker-compose -f ./docker-compose.yml --env-file ${CONFIG} up --build --detach
attach:
	docker attach ${CONTAINER}
stop:
	docker-compose down 
restart:
	docker-compose down && \
	docker-compose -f ./docker-compose.yml --env-file ${CONFIG} up --build --detach
