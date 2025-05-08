# # arguments
ARG BASE_REGISTRY=registry1.dso.mil
ARG BASE_IMAGE=ironbank/opensource/python
ARG BASE_TAG=v3.11

# # base image
FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG}

# install user
USER root

# working directory
WORKDIR /home/webui/

# Copy the tarred model file into the Docker image
COPY models--unstructuredio--yolo_x_layout.tar.gz /tmp/

# Create the destination directory
RUN mkdir -p .cache/huggingface/hub/

# Extract the tar file to the correct location
RUN tar -xzf /tmp/models--unstructuredio--yolo_x_layout.tar.gz -C .cache/huggingface/hub/ && \
    rm /tmp/models--unstructuredio--yolo_x_layout.tar.gz

# Make sure the extracted files have the correct permissions
# (adjust the user/group as needed for your container)
RUN chown -R root:root /home/webui/.cache/huggingface/hub/

# resources
COPY sqlite.tar.gz /tmp
COPY open_webui*.whl /tmp

WORKDIR /home/webui/ocr_build

RUN dnf install -y \
    git gcc gcc-c++ make autoconf automake libtool pkgconfig libtiff-devel\
    wget libpng-devel zlib-devel libwebp-devel \
    && dnf clean all

RUN git clone https://github.com/DanBloomberg/leptonica.git && \
    cd leptonica && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    ldconfig

ENV PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
ENV LIBLEPT_HEADERSDIR=/usr/local/include

# Build and install tesseract
RUN git clone https://github.com/tesseract-ocr/tesseract.git && \
    cd tesseract && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    ldconfig

WORKDIR /home/webui/

RUN dnf upgrade -y --nodocs && \
    dnf install gcc -y && \
    dnf install poppler-utils -y && \
    dnf install mesa-libGL -y && \
    dnf clean all && \
    rm -rf /var/cache/dnf && \
    tar xzf /tmp/sqlite.tar.gz -C /tmp && \
    /tmp/sqlite*/configure --prefix=/usr/local && \
    make && \
    make install && \
    rm -rf /tmp/sqlite* && \
    useradd -r -u 8080 -m -d /home/webui -s /sbin/nologin webui && \
    chown -R webui /home/webui 

# Download and install English language data
RUN mkdir -p /usr/local/share/tessdata && \
    wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata -P /usr/local/share/tessdata

# Set environment variable for Tesseract
ENV TESSDATA_PREFIX=/usr/local/share/tessdata/

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
