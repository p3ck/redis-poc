FROM quay.io/fedora/s2i-core:38

ENV LANG en_US.UTF-8

RUN groupadd -r -g 989 bkr && useradd -rm -g bkr -u 993 -s /bin/bash bkr
RUN mkdir -p /var/cache/bkr-api
RUN chown -R bkr:bkr /var/cache/bkr-api

RUN dnf -y upgrade && \
    rpm --setcaps shadow-utils 2>/dev/null && \
    dnf -y install python3 python3-pip && \
    dnf clean all

COPY --chown=bkr:bkr requirements.txt /opt/bkr-api/requirements.txt
WORKDIR /opt/bkr-api
RUN pip install -r requirements.txt

COPY --chown=bkr:bkr . /opt/bkr-api
#RUN python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt && python3 -m pip cache purge

ENV PYTHONPATH /opt/bkr-api

USER bkr
CMD ["python3", "backend_api.py"]
