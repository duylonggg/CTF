FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    TZ=Etc/UTC

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-flask python3-magic \
        libmagic1 file exiftool poppler-utils \
        ffmpeg libarchive-tools \
        rustc cargo gcc openjdk-17-jre-headless nodejs \
        curl ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY app.py .
COPY templates /srv/templates
COPY secret/flag.txt /flag
RUN chmod 444 /flag
RUN chown -R 1000:1000 /srv

RUN groupadd -g 1000 meta && useradd -u 1000 -g meta -d /srv -s /usr/sbin/nologin meta
USER meta

EXPOSE 8000
ENTRYPOINT ["python3", "/srv/app.py"]
