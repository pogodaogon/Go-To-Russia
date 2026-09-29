# Security and release checks

The MAX webhook is the public user entry point. All other HTTP endpoints use `X-API-Key` in production and are intended only for trusted operators. Do not put this key in a browser, mobile client, or bot message. The webhook uses `X-Max-Bot-Api-Secret`, and requests larger than 1 MiB are rejected.

## Runtime containment and denial-of-service limits

The app container runs as an unprivileged UID, drops Linux capabilities, disallows privilege escalation, uses a read-only root filesystem, and has CPU, memory, PID, temporary-storage, connection-concurrency, and keep-alive limits. PostgreSQL and the app publish their ports only on loopback; PostgreSQL has resource limits and is not published to the public interface. CI validates the Compose configuration.

These controls limit damage from application-level request floods and process compromise. They cannot absorb a volumetric network DDoS. The cloud firewall should allow public inbound TCP 80/443 only, allow SSH TCP 22 only from administrator networks, and deny all other inbound ports for both IPv4 and IPv6. Confirm this in the hosting provider's firewall and use its network DDoS mitigation. Keep an out-of-band console/recovery path before changing SSH or firewall rules. The reverse proxy should cap request/header sizes, request duration, and concurrent connections; do not log webhook bodies or authorization headers. Test legitimate MAX webhook bursts before applying per-IP request limits, since MAX may deliver users through shared address ranges.

The application repository cannot enforce provider firewall rules or host SSH policy. A deployment succeeding does not prove those host controls are enabled; verify them in the hosting control panel and by scanning from an independent external network.

## Before a production launch

1. Set `APP_ENV=production`, use PostgreSQL, and set `API_KEY` and `MAX_WEBHOOK_SECRET` to different random values of at least 32 characters. Configure `MAX_BOT_TOKEN` and an HTTPS `WEBHOOK_PUBLIC_URL` ending in `/webhook/max`.
2. Keep `.env` on the server only. Give it restrictive filesystem permissions. Rotate any token that was ever exposed outside the server.
3. Terminate HTTPS at a reverse proxy. Keep the app and database ports bound to localhost or a private network. Configure request rate limits, access logs without request bodies, and routine backups.
4. Run one app worker while reminders run inside the web process. Multiple workers or replicas need a separate reminder scheduler and distributed delivery lock.
5. Review database changes before deployment. The current additive schema migration is suitable for the MVP but is not a full versioned migration system.
6. Test real MAX webhook delivery, subscription, callbacks, reminders, failure retries, and restoration from a database backup on a staging server.
7. Review catalogue facts for the relevant admission cycle. Unknown tuition and deadlines must remain unknown until an official source confirms them.

## Checks on every change

GitHub Actions runs tests, Python compilation, `pip-audit`, Bandit high-severity checks, a tracked-file secret and data scan, and a Docker build. Dependabot opens dependency update requests weekly. These checks reduce risk but do not replace a staging test or review of infrastructure settings.

For local checks:

```powershell
py -m pip install -r requirements-dev.txt
py -m pytest -q
py -m pip_audit -r requirements-dev.txt --progress-spinner off
py -m bandit -r app -lll -q
py scripts/check_repository_safety.py
```

The repository safety check needs files to be tracked by Git. Never print `.env` or include it in bug reports.
