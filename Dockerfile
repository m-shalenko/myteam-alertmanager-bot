FROM python:3.9-slim-bullseye

WORKDIR /app

RUN apt update -y && apt install ca-certificates curl -y

COPY /app/requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./app/ /app/ 

RUN chmod +x /app/manager.py

USER nobody

ENTRYPOINT [ "/app/manager.py" ]
