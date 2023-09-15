ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY rootfs /
COPY requirements.txt /tmp/requirements.txt

RUN apk --update && \
    apk --no-cache add --update curl python3 py3-pip &&\
    python3 -m pip install --no-cache-dir -r /tmp/requirements.txt




