#ARG BUILD_FROM=homeassistant/amd64-builder
ARG BUILD_FROM=hassioaddons/base
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Copy root filesystem
COPY rootfs /

# Setup base
RUN apk --update upgrade \
  && apk --no-cache add coreutils=8.32-r0 apcupsd mosquitto-clients nmap libxml2-utils sshpass

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="apcupsd2mqtt" \
    io.hass.description="Polling apcupsd services" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="demey <demey@addons.community>" \
    org.opencontainers.image.title="apcupsd2mqtt" \
    org.opencontainers.image.description="Polling apcupsd services" \
    org.opencontainers.image.vendor="Home Assistant Add-on" \
    org.opencontainers.image.authors="demey <demey@addons.community>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://addons.community" \
    org.opencontainers.image.source="https://github.com/demey/hassio-addons/apcupsd2mqtt" \
    org.opencontainers.image.documentation="https://github.com/demey/hassio-addons/blob/master/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
