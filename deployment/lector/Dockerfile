FROM python:3.13.5-slim-bookworm@sha256:4c2cf9917bd1cbacc5e9b07320025bdb7cdf2df7b0ceaccb55e9dd7e30987419

ARG METAXIS_REVISION=development
LABEL org.opencontainers.image.title="METAXIS LECTOR private retrieval service" \
      org.opencontainers.image.source="https://github.com/LittleYeti-Dev/yks2.0-HF-METAXIS" \
      org.opencontainers.image.revision="${METAXIS_REVISION}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LECTOR_HOST=0.0.0.0 \
    LECTOR_PORT=4320

RUN groupadd --gid 10002 lector \
    && useradd --uid 10002 --gid lector --create-home --shell /usr/sbin/nologin lector

WORKDIR /opt/metaxis
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir .

USER 10002:10002
EXPOSE 4320
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:4320/healthz', timeout=2).read()"]
ENTRYPOINT ["metaxis-lector"]
CMD ["serve"]
