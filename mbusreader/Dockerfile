#ARG BUILD_FROM=homeassistant/amd64-builder
ARG BUILD_FROM=hassioaddons/base

FROM ${BUILD_FROM}

# Copy root filesystem
COPY rootfs /

# Setup base
RUN apk --update upgrade \
  && apk --no-cache add coreutils mosquitto-clients libxml2-utils git autoconf automake libtool build-base python3
RUN cd /tmp && git clone https://github.com/rscada/libmbus.git
#RUN chmod /tmp/setup.sh 0755 && /tmp/setup.sh

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
    org.opencontainers.image.source="https://github.com/demey/hassio-addons/mbusreader" \
    org.opencontainers.image.documentation="https://github.com/demey/hassio-addons/blob/master/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}


