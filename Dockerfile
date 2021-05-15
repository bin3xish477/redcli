FROM ubuntu:latest

RUN mkdir awspen
COPY * awspen

CMD ["python", "awspen.py", "-h" ]