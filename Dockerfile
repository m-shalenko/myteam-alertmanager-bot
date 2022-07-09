FROM ubuntu:20.04

WORKDIR /app

COPY ./app/ /app/

RUN apt update -y && apt install ca-certificates curl python3.8 python3-pip -y && \
    pip3 install -r requirements.txt && \
    chmod +x /app/manager.py

USER nobody
ENTRYPOINT [ "/app/manager.py" ]
