FROM ubuntu:24.04

ARG INTERNAL_REPO_URL="github.com/intel-innersource/applications.ai.enterprise-rag.enterprise-ai-solution.git"
ARG GITHUB_PAT
ARG COV_USER
ARG COV_PASS

ENV PYTHON_REQUIRED_CHECKERS="--webapp-security --enable-audit-checkers --enable-default"
ENV JS_REQUIRED_CHECKERS="--checker-option DOM_XSS:distrust_all:true"

ARG IPAS_REPO_URL="github.com/intel-innersource/applications.analyzers.code.static.coverity-support.git"
ARG IPAS_VERSION="1.6"

RUN apt update && apt install -y wget git curl python3 python3-pip

# Download and install certificates

WORKDIR /downloads

RUN curl http://pki.intel.com/crt/IntelSHA256RootCA.crt > IntelSHA256RootCA.crt && \
    curl http://certificates.intel.com/repository/certificates/Intel%20Root%20CA.crt > IntelRootCA.crt && \
    openssl x509 -inform der -in IntelSHA256RootCA.crt -outform pem -out /usr/local/share/ca-certificates/IntelSHA256RootCA-base64.crt && \
    openssl x509 -inform der -in IntelRootCA.crt -outform pem -out /usr/local/share/ca-certificates/IntelRootCA-base64.crt && \
    update-ca-certificates

# Download and install Coverity

RUN wget -q https://af-amr01.devtools.intel.com/artifactory/coverity-or-local/Enterprise/license.dat

RUN wget -q https://af-amr01.devtools.intel.com/artifactory/coverity-or-local/Enterprise/cov-analysis-linux64-2025.3.0.sh
RUN chmod +x cov-analysis-linux64-2025.3.0.sh
RUN ./cov-analysis-linux64-2025.3.0.sh -q \
    --installation.dir=/coverity/analysis \
    --license.agreement=agree --license.region=0 --license.type.choice=0 \
    --license.cov.path=/downloads/license.dat --component.sdk=false \
    --component.skip.documentation=true

WORKDIR /repo
RUN git clone https://${GITHUB_PAT}@${INTERNAL_REPO_URL} .

# Configure coverity and run the scan

ENV PATH="/coverity/analysis/bin:${PATH}"
RUN cov-configure --python
RUN cov-configure --javascript
RUN git ls-files > scm_files.lst
RUN coverity capture --dir idir
RUN cov-analyze --dir idir $PYTHON_REQUIRED_CHECKERS $JS_REQUIRED_CHECKERS

# Commit
RUN echo "${COV_USER}" > test.txt
RUN cov-commit-defects --dir idir --stream "Enterprise-RAG" --url https://coverity.devtools.intel.com/prod15 --user ${COV_USER} --password ${COV_PASS} --strip-path `pwd` --noxrefs

# Pull IPAS repo
WORKDIR /ipas
RUN git clone https://${GITHUB_PAT}@${IPAS_REPO_URL} .
RUN git checkout v${IPAS_VERSION}

# Configure IPAS
COPY cov-report-ipas-conf.yaml /ipas/Scripts/github_actions/ipas_report/

WORKDIR /ipas/Scripts/github_actions/ipas_report
RUN pip3 install --break-system-packages -r requirements.txt
RUN mkdir -p report
RUN python3 IPAS_SAST_Report_Tool.py cov-report-ipas-conf.yaml --output report/output.html --user ${COV_USER} --password ${COV_PASS}

ENTRYPOINT ["/bin/bash"]
