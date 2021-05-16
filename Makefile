help:
	python awsredcli.py --help

clean:
	rm keys

docker-test:
	docker build \
	--tag=awsredcli \
	--file=./Dockerfile
	docker run \
	--name=awsredcli
	awsredcli