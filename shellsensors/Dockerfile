ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy root filesystem
COPY rootfs /

# Setup base
RUN apk --update upgrade && \
    apk --no-cache add perl perl-net-ssleay perl-crypt-ssleay perl-lwp-useragent-determined perl-lwp-protocol-https

RUN apk add --no-cache --virtual .build-deps gcc make build-base perl-dev && \
    echo 'yes' | perl -MCPAN -e 'install (JSON::Parse)' && \
    apk del .build-deps    

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="shellsensors" \
    io.hass.description="Adding different types of shell sensors to HA" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="demey <demey@addons.community>" \
    org.opencontainers.image.title="mbusreader" \
    org.opencontainers.image.description="Adding different types of shell sensors to HA" \
    org.opencontainers.image.vendor="Home Assistant Add-on" \
    org.opencontainers.image.authors="demey <demey@addons.community>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://addons.community" \
    org.opencontainers.image.source="https://github.com/demey/hassio-addons/tree/master/shellsensors" \
    org.opencontainers.image.documentation="https://github.com/demey/hassio-addons/blob/master/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}


