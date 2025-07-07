ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Setup base
RUN apk --update upgrade && \
    apk add --no-cache \
        curl \
        mosquitto-clients \
        perl \
        perl-net-ssleay \
        perl-crypt-ssleay \
        perl-lwp-useragent-determined \
        perl-lwp-protocol-https \
        perl-file-slurp \
        apache-mod-fcgid \
        perl-fcgi \
        perl-cgi \
        perl-switch \
        perl-utils \
        python3 \
        py3-urllib3 \
        py3-paho-mqtt \
        py3-pip \
        perl-switch \
    \
    && apk add --no-cache --virtual .build-dependencies \
        gcc \
        make \
        build-base \
        perl-dev \
    &&  cpan JSON::Parse \
#    && echo 'yes' | perl -MCPAN -e 'install (JSON::Parse)' \
    \
    && apk del --no-cache --purge .build-dependencies \
    \
    && sed -i 's,^ServerRoot .*,ServerRoot /share/apache2,g' /etc/apache2/httpd.conf \
    && sed -i 's,^Listen .*,Listen 8001,g' /etc/apache2/httpd.conf \
    && sed -i 's,^DocumentRoot ".*,DocumentRoot "/share/apache2/html",g' /etc/apache2/httpd.conf \
    && sed -i 's,Directory "/var/www/localhost/htdocs.*,Directory "/share/apache2/html">,g' /etc/apache2/httpd.conf \
    && sed -i 's,/var/www/localhost/cgi-bin,/share/apache2/cgi-bin,g' /etc/apache2/httpd.conf \    
    && sed -i 's,Options None,Options ExecCGI,g' /etc/apache2/httpd.conf \
    && sed -i 's,Require all granted,Require all granted\n    AddHandler cgi-script .pl .py,g' /etc/apache2/httpd.conf \
    && sed -i 's,#LoadModule cgi,LoadModule cgi,g' /etc/apache2/httpd.conf \
    && sed -i 's,/var/log/apache2/,/share/apache2/logs/,g' /etc/logrotate.d/apache2

# Copy root filesystem
COPY rootfs /

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="apache2-perl-server" \
    io.hass.description="Apache HTTP Server" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="demey <demey@addons.community>" \
    org.opencontainers.image.title="apache2-perl-server" \
    org.opencontainers.image.description="Apache HTTP Server" \
    org.opencontainers.image.vendor="Home Assistant Add-on" \
    org.opencontainers.image.authors="demey <demey@addons.community>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://addons.community" \
    org.opencontainers.image.source="https://github.com/demey/hassio-addons/tree/master/apache2-perl-server" \
    org.opencontainers.image.documentation="https://github.com/demey/hassio-addons/blob/master/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}


