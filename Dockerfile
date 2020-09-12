FROM python:3.8-slim

ADD . /tidypy
WORKDIR /tidypy

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        bzr \
        git \
        mercurial \
        subversion && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir . Sphinx

VOLUME /project
WORKDIR /project
CMD ["tidypy", "check"]

