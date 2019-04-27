FROM python:3.7-alpine

ADD . /tidypy
WORKDIR /tidypy

RUN apk --no-cache add git mercurial subversion bzr gcc musl-dev && \
    pip install --no-cache-dir . Sphinx

VOLUME /project
WORKDIR /project
CMD ["tidypy", "check"]

