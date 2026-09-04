ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY rootfs /
COPY requirements.txt /tmp/requirements.txt

RUN apk add --no-cache curl tzdata && \
    python3 -m pip install --no-cache-dir -r /tmp/requirements.txt
