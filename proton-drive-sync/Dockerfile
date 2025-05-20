ARG BUILD_FROM
FROM ${BUILD_FROM}

COPY rootfs /
RUN apk update && \
    apk add --no-cache rclone
