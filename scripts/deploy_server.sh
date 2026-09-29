#!/usr/bin/env bash
set -Eeuo pipefail

cd /opt/uniroute
docker compose up -d --build --remove-orphans

for attempt in $(seq 1 30); do
    if curl --fail --silent http://127.0.0.1:8000/health >/dev/null; then
        echo "Deployment healthy"
        exit 0
    fi
    sleep 2
done

docker compose ps
docker compose logs --tail=80 app
echo "Application did not become healthy after deployment" >&2
exit 1
