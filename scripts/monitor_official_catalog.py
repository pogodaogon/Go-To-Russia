"""Discover MTUCI programme updates; never modify the live catalogue."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.seed import CATALOG


PROGRAMS_URL = "https://en.mtuci.ru/academics/undergraduate_programmes/"
INTERNATIONAL_URL = "https://en.mtuci.ru/education/intern_edu/"
MEPHI_PROGRAMS_URL = "https://eng.mephi.ru/academics/degrees-and-programs/ba"
MEPHI_ADMISSIONS_URL = "https://eng.mephi.ru/academics/admissions"
ALLOWED_HOSTS = {
    "admissions.hse.ru", "en.mai.ru", "en.mtuci.ru", "eng.mephi.ru",
    "eng.mipt.ru", "fgp.msu.ru", "www.hse.ru", "www.sechenov.ru",
}
MAX_PAGE_BYTES = 6 * 1024 * 1024
OFFICIAL_SOURCE_URLS = sorted({
    str(item[key])
    for item in CATALOG
    for key in ("source", "admissions_url")
    if item.get(key)
})


class PageSnapshotParser(HTMLParser):
    """Keep a small text index and title for human review of monitored pages."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        clean = " ".join(data.split())
        if clean:
            if self._in_title:
                self.title = (self.title + " " + clean).strip()
            self.text.append(clean)


class OfficialPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page_text: list[str] = []
        self.programs: list[dict[str, object]] = []
        self._depth = 0
        self._card: dict[str, object] | None = None
        self._capture: str | None = None
        self._capture_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        classes = set((attr.get("class") or "").split())
        if tag == "div" and self._card is None and "specialty" in classes:
            self._card = {"code": "", "name": "", "tracks": []}
            self._depth = 1
        elif self._card is not None and tag == "div":
            self._depth += 1

        if self._card is not None and tag == "p":
            if "specialty__code" in classes:
                self._capture = "code"
            elif "specialty__title" in classes:
                self._capture = "name"
            elif "title" in classes:
                self._capture = "track"
            if self._capture:
                self._capture_depth = self._depth
                self._parts = []

    def handle_endtag(self, tag: str) -> None:
        if self._capture and tag == "p":
            value = " ".join("".join(self._parts).split())
            if value:
                if self._capture == "track":
                    tracks = self._card["tracks"]
                    if isinstance(tracks, list):
                        tracks.append(value)
                else:
                    self._card[self._capture] = value
            self._capture = None
            self._parts = []
        if self._card is not None and tag == "div":
            self._depth -= 1
            if self._depth == 0:
                if self._card.get("code") and self._card.get("name"):
                    self.programs.append(self._card)
                self._card = None

    def handle_data(self, data: str) -> None:
        clean = " ".join(data.split())
        if clean:
            self.page_text.append(clean)
        if self._capture:
            self._parts.append(data)


class MephiTableParser(HTMLParser):
    """Read programme rows under bachelor (03.xx) headings."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page_text: list[str] = []
        self.programs: list[dict[str, str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._current_code = ""
        self._current_name = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._row = []
        elif tag == "td" and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self._finish_row()
            self._row = None

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            self.page_text.append(value)
        if self._cell is not None:
            self._cell.append(data)

    def _finish_row(self) -> None:
        cells = self._row or []
        row_text = " ".join(cells).replace("\ufeff", "")
        code_match = re.search(r"\b(\d{2}\.\d{2}\.\d{2})\b", row_text)
        if code_match:
            code = code_match.group(1)
            self._current_code = code if ".03." in code else ""
            self._current_name = row_text.split(code, 1)[-1].strip()
            return
        if not self._current_code or len(cells) < 5 or not cells[0].isdigit() or not cells[1]:
            return
        language = cells[4].strip()
        if language.casefold() in {"russian", "english"}:
            self.programs.append({"code": self._current_code, "programme": self._current_name, "track": cells[1], "language": language})


def normalize_track(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()
    value = re.sub(r"\bsystems\b", "system", value)
    value = re.sub(r"\btechnologies\b", "technology", value)
    value = re.sub(r"\bnetworks\b", "network", value)
    return " ".join(value.split())


def _fetch(client: httpx.Client, url: str, parser_type=OfficialPageParser):
    if urlparse(url).scheme != "https" or urlparse(url).hostname not in ALLOWED_HOSTS or urlparse(url).username or urlparse(url).password:
        raise RuntimeError(f"Official source URL is outside the HTTPS allowlist: {url}")
    response = client.get(url, follow_redirects=True)
    response.raise_for_status()
    final_host = urlparse(str(response.url)).hostname
    if final_host not in ALLOWED_HOSTS or final_host != urlparse(url).hostname:
        raise RuntimeError(f"Official source redirected to an unapproved host: {final_host}")
    if len(response.content) > MAX_PAGE_BYTES:
        raise RuntimeError(f"Official source exceeded the {MAX_PAGE_BYTES}-byte limit: {url}")
    parser = parser_type()
    parser.feed(response.text)
    return parser


def discover() -> dict[str, object]:
    with httpx.Client(timeout=httpx.Timeout(20), headers={"User-Agent": "UniRouteCatalogMonitor/1.0"}) as client:
        programs_page = _fetch(client, PROGRAMS_URL)
        foreign_page = _fetch(client, INTERNATIONAL_URL)
        mephi_page = _fetch(client, MEPHI_PROGRAMS_URL, MephiTableParser)
        mephi_admissions = _fetch(client, MEPHI_ADMISSIONS_URL)
        source_checks = []
        signal_pattern = re.compile(r"programme|program|admission|bachelor|degree|language|tuition|deadline|information security|cybersecurity", re.I)
        for source_url in OFFICIAL_SOURCE_URLS:
            try:
                page = _fetch(client, source_url, PageSnapshotParser)
                signal_lines = [line[:240] for line in page.text if signal_pattern.search(line)][:30]
                source_checks.append({
                    "source": source_url,
                    "status": "reachable_needs_human_review",
                    "title": page.title,
                    "sha256": hashlib.sha256(" ".join(page.text).encode("utf-8")).hexdigest(),
                    "signals": signal_lines,
                })
            except (httpx.HTTPError, RuntimeError, ValueError) as exc:
                source_checks.append({
                    "source": source_url,
                    "status": "unavailable_needs_human_review",
                    "error_type": type(exc).__name__,
                })

    language_evidence = " ".join(foreign_page.page_text).casefold()
    if "all educational programs for foreign citizens are conducted in russian" not in language_evidence:
        raise RuntimeError("Could not confirm the international-student language statement on MTUCI's official page")

    existing = {
        (str(item.get("source_code", "")), normalize_track(str(item.get("source_track", ""))))
        for item in CATALOG
        if urlparse(str(item.get("source", ""))).hostname in ALLOWED_HOSTS and item.get("source_code") and item.get("source_track")
    }
    records = []
    for item in programs_page.programs:
        tracks = item.get("tracks") or [item["name"]]
        for track in tracks:
            key = (str(item["code"]), normalize_track(str(track)))
            records.append({
                "code": item["code"],
                "programme": item["name"],
                "track": track,
                "language_for_foreign_applicants": "russian",
                "catalog_status": "catalogued" if key in existing else "review_candidate",
                "source": PROGRAMS_URL,
                "language_source": INTERNATIONAL_URL,
                "intake_cycle": "not stated on the source page; confirm before publishing",
            })

    mephi_text = " ".join(mephi_admissions.page_text).casefold()
    if "admission" not in mephi_text or not mephi_page.programs:
        raise RuntimeError("Could not confirm MEPhI programme/admissions content on official pages")
    for item in mephi_page.programs:
        key = (item["code"], normalize_track(item["track"]))
        records.append({
            "code": item["code"], "programme": item["programme"], "track": item["track"],
            "language_for_foreign_applicants": item["language"].casefold(),
            "catalog_status": "catalogued" if key in existing else "review_candidate",
            "source": MEPHI_PROGRAMS_URL, "language_source": MEPHI_PROGRAMS_URL,
            "intake_cycle": "not stated on the source page; confirm before publishing",
        })

    if not records:
        raise RuntimeError("No programme entries were found on official programme pages")
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "universities": ["Moscow Technical University of Communications and Informatics", "National Research Nuclear University MEPhI"],
        "programmes_seen": len(records),
        "review_candidates": sum(item["catalog_status"] == "review_candidate" for item in records),
        "source_pages_checked": len(source_checks),
        "source_pages_unavailable": sum(item["status"].startswith("unavailable") for item in source_checks),
        "source_checks": source_checks,
        "records": records,
    }


def render_markdown(report: dict[str, object]) -> str:
    def safe_markdown(value: object) -> str:
        cleaned = " ".join(str(value).split())
        cleaned = cleaned.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return re.sub(r"([\\`*_{}\[\]()#+\-.!|])", r"\\\1", cleaned)

    records = report["records"]
    lines = [
        "## Official catalogue monitor ? MTUCI and MEPhI",
        f"Checked {report['generated_at_utc']}. Found {report['programmes_seen']} programme tracks; {report['review_candidates']} need review.",
        "All findings are candidates only. This job never edits or publishes the application catalogue.",
        f"Official source pages checked: {report['source_pages_checked']}; inaccessible pages requiring follow-up: {report['source_pages_unavailable']}.",
        "Source titles, matching text snippets, and SHA-256 fingerprints are attached to the JSON report so moderators can compare weekly changes.",
        "",
    ]
    for item in records:
        state = "catalogued" if item["catalog_status"] == "catalogued" else "review candidate"
        lines.append(
            f"- **{state}** — {safe_markdown(item['code'])} {safe_markdown(item['programme'])}: "
            f"{safe_markdown(item['track'])} ({safe_markdown(item['language_for_foreign_applicants'])} for foreign applicants; intake cycle not stated)."
        )
    lines.extend(("", f"Sources: [MTUCI programme list]({PROGRAMS_URL}), [MTUCI international admissions]({INTERNATIONAL_URL}), [MEPhI bachelor's programmes]({MEPHI_PROGRAMS_URL}), [MEPhI admissions]({MEPHI_ADMISSIONS_URL})."))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output-json", type=Path, help="also save the machine-readable moderation report")
    args = parser.parse_args()
    report = discover()
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(render_markdown(report) if args.format == "markdown" else json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
