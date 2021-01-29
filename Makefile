.PHONY: all start attach stop restart
CONFIG=config/config.env
include ${CONFIG}                                                                                    

all: start 
start:
	docker-compose -f ./docker-compose.yml --env-file ${CONFIG} up --build --detach
attach:
	docker attach ${CONTAINER}
stop: 
	docker-compose down 
restart: stop start
