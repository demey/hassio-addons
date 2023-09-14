ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

LABEL \
    io.hass.name="ha2gd" \
    io.hass.description="Sync folders with google drive" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="demey <demey@addons.community>" \
    org.opencontainers.image.title="ha2gd" \
    org.opencontainers.image.description="Sync folders with Google Drive" \
    org.opencontainers.image.vendor="Home Assistant Add-on" \
    org.opencontainers.image.authors="demey <demey@addons.community>" \
    org.opencontainers.image.source="https://github.com/demey/hassio-addons/tree/master/ha2gd" \
    org.opencontainers.image.documentation="https://github.com/demey/hassio-addons/blob/master/README.md" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://addons.community" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}

COPY rootfs /
RUN apk add --no-cache python3 py3-pip && \
    python3 -m pip install --no-cache-dir pydrive