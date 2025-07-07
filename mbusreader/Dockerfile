ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy root filesystem
COPY rootfs /

# Setup base
RUN apk --update upgrade && \
    apk --no-cache add coreutils mosquitto-clients libxml2-utils git python3 py3-pip && \
    pip install jc jq && \
    cd /tmp && git clone https://github.com/rscada/libmbus.git
RUN apk add --no-cache --virtual .build-deps autoconf automake libtool build-base && \
    chmod u+x /tmp/libmbus/build.sh && \
    cd /tmp/libmbus && \
    ./build.sh && \
    ./configure && \
    make -j4 && \
    make install && \
    apk del .build-deps    
RUN cd /tmp && rm -rf /tmp/libmbus

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="mbusreader" \
    io.hass.description="Reading data from USB to MBus Master Module" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="demey <demey@addons.community>" \
    org.opencontainers.image.title="mbusreader" \
    org.opencontainers.image.description="Reading data from USB to MBus Master Module" \
    org.opencontainers.image.vendor="Home Assistant Add-on" \
    org.opencontainers.image.authors="demey <demey@addons.community>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://addons.community" \
    org.opencontainers.image.source="https://github.com/demey/hassio-addons/tree/master/mbusreader" \
    org.opencontainers.image.documentation="https://github.com/demey/hassio-addons/blob/master/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}


