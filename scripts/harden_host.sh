#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
    echo "Run this script as root" >&2
    exit 1
fi
if [[ ! -s /root/.ssh/authorized_keys ]]; then
    echo "Refusing SSH hardening: root has no authorized SSH key" >&2
    exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq ufw fail2ban unattended-upgrades

cat > /etc/ssh/sshd_config.d/00-local-hardening.conf <<'EOF'
PermitRootLogin prohibit-password
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitEmptyPasswords no
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no
AllowStreamLocalForwarding no
MaxAuthTries 3
LoginGraceTime 30
ClientAliveInterval 300
ClientAliveCountMax 2
MaxStartups 10:30:60
EOF

sshd -t
effective_ssh_config="$(sshd -T)"
grep -qx 'permitrootlogin without-password' <<<"${effective_ssh_config}"
grep -qx 'passwordauthentication no' <<<"${effective_ssh_config}"
grep -qx 'x11forwarding no' <<<"${effective_ssh_config}"
grep -qx 'maxstartups 10:30:60' <<<"${effective_ssh_config}"

ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH admin and restricted GitHub deployment'
ufw allow 80/tcp comment 'HTTP redirect to HTTPS'
ufw allow 443/tcp comment 'HTTPS public bot webhook'
ufw logging low
ufw --force enable

cat > /etc/fail2ban/jail.d/sshd-hardening.local <<'EOF'
[sshd]
enabled = true
backend = systemd
maxretry = 5
findtime = 10m
bantime = 1h
EOF
systemctl enable --now fail2ban
fail2ban-client status sshd

cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF
systemctl enable --now apt-daily.timer apt-daily-upgrade.timer

install -d -m 755 /etc/systemd/system/caddy.service.d
cat > /etc/systemd/system/caddy.service.d/10-resource-limits.conf <<'EOF'
[Service]
Restart=on-failure
RestartSec=3s
TimeoutStopSec=30s
MemoryMax=768M
CPUQuota=150%
TasksMax=256
EOF
systemctl daemon-reload
systemctl restart caddy

systemctl reload ssh
ufw status verbose
systemctl is-active fail2ban apt-daily.timer apt-daily-upgrade.timer caddy
echo "Host baseline applied; SSH is key-only for root, only 22/80/443 are allowed, security updates are scheduled, and Caddy has resource/restart limits."
