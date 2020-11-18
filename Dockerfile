FROM python:3.8-slim-buster
RUN apt-get update; apt-get install -y curl && mkdir /src
WORKDIR /src
ENV PYTHONPATH "${PYTHONPATH}:/src/"
ENV PATH "/src/scripts:${PATH}"
COPY . /src
RUN pip install poetry && poetry config virtualenvs.create false && poetry update --no-dev && poetry shell
RUN chmod +x /src/scripts/*
ENTRYPOINT ["docker-entrypoint.sh"]