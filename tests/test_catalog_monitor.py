from scripts.monitor_official_catalog import ALLOWED_HOSTS, OFFICIAL_SOURCE_URLS, OfficialPageParser, PageSnapshotParser, normalize_track, render_markdown
from app.db import Base
from app.models import Program, University
from app.seed import seed_database
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session


def test_official_page_parser_extracts_programme_tracks():
    parser = OfficialPageParser()
    parser.feed(
        '<div class="specialty"><p class="specialty__code">10.03.01</p>'
        '<p class="specialty__title">Information security</p>'
        '<div class="nested"><p class="title">Computer system security</p></div></div>'
    )
    assert parser.programs == [{"code": "10.03.01", "name": "Information security", "tracks": ["Computer system security"]}]


def test_official_track_matching_normalizes_common_plural_variants():
    assert normalize_track("Computer system security") == normalize_track("Computer systems security")


def test_source_monitor_uses_only_allowlisted_https_urls_and_keeps_page_signals():
    from urllib.parse import urlparse

    assert len(OFFICIAL_SOURCE_URLS) == 16
    assert all(urlparse(url).scheme == "https" and urlparse(url).hostname in ALLOWED_HOSTS for url in OFFICIAL_SOURCE_URLS)
    parser = PageSnapshotParser()
    parser.feed("<html><title>Official admissions page</title><p>English language programme</p></html>")
    assert parser.title == "Official admissions page"
    assert "English language programme" in parser.text


def test_catalog_report_uses_detected_language_and_escapes_remote_markdown():
    report = {
        "generated_at_utc": "2026-09-30T00:00:00+00:00",
        "programmes_seen": 1,
        "review_candidates": 1,
        "source_pages_checked": 0,
        "source_pages_unavailable": 0,
        "records": [{
            "catalog_status": "review_candidate", "code": "10.03.01",
            "programme": "Information [Security]", "track": "Track <img src=x>",
            "language_for_foreign_applicants": "english",
        }],
    }
    rendered = render_markdown(report)
    assert "english for foreign applicants" in rendered
    assert "\\[Security\\]" in rendered
    assert "<img" not in rendered


def test_mephi_table_parser_extracts_bachelor_track_language():
    from scripts.monitor_official_catalog import MephiTableParser

    parser = MephiTableParser()
    parser.feed(
        "<table><tr><td>10.03.01</td><td>Information Security</td></tr>"
        "<tr><td>1</td><td>Computer systems security</td><td>Moscow</td><td>4 years</td><td>Russian</td></tr></table>"
    )
    assert parser.programs == [{"code": "10.03.01", "programme": "Information Security", "track": "Computer systems security", "language": "Russian"}]


def test_seed_keeps_programme_universities_at_detailed_catalog_level():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed_database(db)
        assert db.scalar(select(func.count(University.id))) == 30
        assert db.scalar(select(func.count(University.id)).where(University.catalog_level == "detailed")) == 7
        assert db.scalar(select(func.count(Program.id)).where(Program.listed.is_(True))) == 29
        universities_with_programmes = db.scalars(select(University).join(Program)).all()
        assert all(university.catalog_level == "detailed" for university in universities_with_programmes)
