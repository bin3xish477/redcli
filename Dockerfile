FROM ubuntu:latest

RUN apt update -y
RUN apt install python3 python3-pip -y

RUN mkdir /redcli
COPY . /redcli
WORKDIR /redcli
RUN pip install -r /redcli/requirements.txt

CMD ["python3", "redcli.py", "aws", "--help" ]