ARG BUILD_FROM
FROM --platform=linux/amd64 ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY rootfs /
COPY requirements.txt /tmp/requirements.txt

RUN apk --update upgrade && \
    apk add --no-cache curl python3 py3-pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt
