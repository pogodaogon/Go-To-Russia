"""Fail CI when tracked files contain common secret material or runtime data."""

from pathlib import Path
import re
import subprocess
import sys


FORBIDDEN_NAMES = {".env", ".git-credentials", "id_rsa", "id_ed25519"}
FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".log", ".key", ".p12", ".pfx"}
SECRET_PATTERNS = {
    "private key": re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})"),
    "API token": re.compile(rb"(?:sk-[A-Za-z0-9_-]{30,}|xox[baprs]-[A-Za-z0-9-]{20,})"),
    "configured secret": re.compile(rb"(?m)^[ \t]*(?:MAX_BOT_TOKEN|MAX_WEBHOOK_SECRET|API_KEY|LLM_API_KEY)[ \t]*=[ \t]*[^\s#]+"),
}


def main() -> int:
    result = subprocess.run(["git", "ls-files", "-z"], check=True, capture_output=True)
    tracked = [Path(raw.decode("utf-8")) for raw in result.stdout.split(b"\0") if raw]
    if not tracked:
        print("No tracked files to inspect", file=sys.stderr)
        return 1
    findings = []
    for path in tracked:
        name = path.name.lower()
        if name in FORBIDDEN_NAMES or (name.startswith(".env.") and name != ".env.example") or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(f"{path}: forbidden runtime or secret file")
            continue
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        content = path.read_bytes()
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                findings.append(f"{path}: possible {label}")
    for finding in findings:
        print(finding, file=sys.stderr)
    if findings:
        return 1
    print(f"Checked {len(tracked)} tracked files for forbidden files and common secrets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
