ARG BUILD_FROM
FROM ${BUILD_FROM}

COPY rootfs /
RUN apk update && \
    apk add --no-cache python3 py3-pip && \
    python3 -m pip install --no-cache-dir pydrive