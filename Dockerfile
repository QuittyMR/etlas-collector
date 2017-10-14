#Version 1.0
FROM python:3.6.1
MAINTAINER Tomer Raz <qtomerr@gmail.com>

ENV APP_NAME scraper-collector
ENV APP_HOME /opt/scraper-collector

RUN apt-get update -y && \
    apt-get install -y --force-yes \
	freetds-dev \
	libffi-dev \
	libssl-dev \
	libmemcached-dev \
	python-pip \
	telnet \
        && rm -rf /var/lib/apt/lists/*

RUN mkdir ${APP_HOME}
WORKDIR ${APP_HOME}

ADD ./dist .
RUN pip install wheel
RUN pip install --use-wheel --find-links=. scraper-collector

RUN mkdir logs

ADD ./resources ./resources
## Run stuff
EXPOSE 9041
STOPSIGNAL SIGTERM

ENV PATH ${PATH}:${APP_HOME}
CMD scraper-collector
