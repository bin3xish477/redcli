help:
	python3 redcli.py --help

clean:
	rm ./keys

docker-run:
	docker build \
	--tag=redcli .\
	&& docker run \
	--name=redcli \
	-it --entrypoint=/bin/bash \
	redcli