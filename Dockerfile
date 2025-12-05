FROM python:3.11-slim AS builder
WORKDIR /install
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy requirements and install into /install
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN pip3 install --prefix=/install -r requirements.txt

# ---------- stage: runtime ----------
FROM python:3.11-slim AS runtime
ENV TZ=UTC
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install runtime deps (cron, tzdata)
RUN apt-get update && apt-get install -y --no-install-recommends cron tzdata dos2unix && \
    ln -fs /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy installed python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app ./app
COPY scripts ./scripts
COPY cron ./cron
COPY entrypoint.sh ./entrypoint.sh
COPY student_private.pem ./student_private.pem
COPY student_public.pem ./student_public.pem
COPY instructor_public.pem ./instructor_public.pem
COPY requirements.txt ./requirements.txt
COPY .gitattributes .gitattributes

# Ensure scripts are executable and cron file uses LF
RUN chmod +x /app/entrypoint.sh && dos2unix /app/cron/2fa-cron || true

# Create volumes
VOLUME ["/data", "/cron"]

# Expose port
EXPOSE 8080

# Use a non-root user? (optional) — for simplicity run as root here
CMD ["/app/entrypoint.sh"]
