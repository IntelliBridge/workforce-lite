ARG BASE_REGISTRY=registry1.dso.mil
ARG BASE_IMAGE=ironbank/redhat/ubi/ubi9
ARG BASE_TAG=9.5

FROM docker.io/opensearchproject/opensearch:2.19.1 as source

FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG}

ARG UID=1000
ARG GID=1000
ARG OPENSEARCH_HOME=/usr/share/opensearch

RUN dnf update -y --nodocs && \
    dnf install -y tar && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Create an opensearch user, group
RUN groupadd -g $GID opensearch && \
    adduser -u $UID -g $GID -d $OPENSEARCH_HOME opensearch

COPY --from=source --chown=$UID:$GID $OPENSEARCH_HOME $OPENSEARCH_HOME

WORKDIR $OPENSEARCH_HOME

# Set $JAVA_HOME
RUN echo "export JAVA_HOME=$OPENSEARCH_HOME/jdk" >> /etc/profile.d/java_home.sh && \
    echo "export PATH=\$PATH:\$JAVA_HOME/bin" >> /etc/profile.d/java_home.sh && \
    ls -l $OPENSEARCH_HOME

ENV JAVA_HOME=$OPENSEARCH_HOME/jdk
ENV PATH=$PATH:$JAVA_HOME/bin:$OPENSEARCH_HOME/bin
ENV LD_LIBRARY_PATH=/usr/share/opensearch/plugins/opensearch-knn/lib


# Change user
USER $UID

# Setup OpenSearch
# Disable security demo installation during image build, and allow user to disable during startup of the container
# Enable security plugin during image build, and allow user to disable during startup of the container
ARG DISABLE_INSTALL_DEMO_CONFIG=true
ARG DISABLE_SECURITY_PLUGIN=false
RUN ./opensearch-onetime-setup.sh

# Remove vulnerable spark JARs (CVE-2018-17190)
RUN rm /usr/share/opensearch/plugins/opensearch-skills/spark*

# Expose ports for the opensearch service (9200 for HTTP and 9300 for internal transport) and performance analyzer (9600 for the agent and 9650 for the root cause analysis component)
EXPOSE 9200 9300 9600 9650

# CMD to run
ENTRYPOINT ["./opensearch-docker-entrypoint.sh"]
CMD ["opensearch"]
