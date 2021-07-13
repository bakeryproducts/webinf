# Web viewer for images
Tile viewer for images, based on leaflet, GDAL, flask and docker

# TODO
 - embedding description in generate page
 - clickable tile for neighbour search
 - tree structure for landing page
 - more generate settings, name set
 - heatmap for distance?
 - inverse neighbouring, most distant objects
 - fix for cosine dist 
 - embedder readme


# Dependencies
docker
make

# Usage
TODO : In folder containing big_img.tif:

1. Copy big_img.tif  to mount folder, (./data)

2. 
 - `make start` 
        will start containers, check http://localhost:7088
 - `make stop`
        will stop containers
 - `make restart`
        ...


