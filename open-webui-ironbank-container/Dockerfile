# arguments
ARG BASE_REGISTRY=registry1.dso.mil
ARG BASE_IMAGE=ironbank/opensource/python
ARG BASE_TAG=v3.11

# base image
FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG}

# install user
USER root

# working directory
WORKDIR /home/webui

# resources
COPY sqlite.tar.gz /tmp
COPY open_webui*.whl /tmp

RUN dnf upgrade -y --nodocs && \
    dnf install gcc -y && \
    dnf install poppler-utils -y && \
    dnf install mesa-libGL -y && \
    dnf install python3-opencv -y && \
    dnf clean all && \
    rm -rf /var/cache/dnf && \
    tar xzf /tmp/sqlite.tar.gz -C /tmp && \
    /tmp/sqlite*/configure --prefix=/usr/local && \
    make && \
    make install && \
    rm -rf /tmp/sqlite* && \
    useradd -r -u 8080 -m -d /home/webui -s /sbin/nologin webui && \
    chown -R webui /home/webui 

USER webui

COPY requirements.txt /home/webui/

RUN pip install --user --no-cache-dir --timeout=5000 -r requirements.txt

# ports
EXPOSE 8080

# environment variables
ENV LD_LIBRARY_PATH=/usr/local/lib
ENV PATH=/home/webui/.local/bin:$PATH
ENV HOST=0.0.0.0
ENV PORT=8080

# initialize
ENTRYPOINT ["open-webui", "serve"]
