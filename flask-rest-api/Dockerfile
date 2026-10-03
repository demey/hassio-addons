ARG BUILD_FROM
FROM --platform=linux/amd64 ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY rootfs /
COPY requirements.txt /tmp/requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        python3 \
        python3-pip \
        python3-venv \
        ssocr \
        libgl1 \
        libglib2.0-0 && \
    pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/*
