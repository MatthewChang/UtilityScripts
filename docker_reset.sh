docker-machine rm default -y
docker-machine create default --driver virtualbox
eval $(docker-machine env default)
