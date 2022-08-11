.PHONY: all start attach stop restart
CONFIG=config/config.env
include ${CONFIG}                                                                                    

all: start 
start:
	docker-compose --env-file ${CONFIG} up webserver tiler nginx labeler
start-all:
	docker-compose --env-file ${CONFIG} up 
build:
	docker-compose --env-file ${CONFIG} build
attach:
	docker attach ${CONTAINER}
stop: 
	docker-compose --env-file ${CONFIG} kill
restart: stop start
