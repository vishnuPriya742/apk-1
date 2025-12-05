set -e


if [ -f /app/cron/2fa-cron ]; then
  crontab /app/cron/2fa-cron
fi

mkdir -p /data /cron
chmod 755 /data /cron
service cron start || cron -f &
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
