from scripts.monitor_official_catalog import OfficialPageParser, normalize_track


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


def test_mephi_table_parser_extracts_bachelor_track_language():
    from scripts.monitor_official_catalog import MephiTableParser

    parser = MephiTableParser()
    parser.feed(
        "<table><tr><td>10.03.01</td><td>Information Security</td></tr>"
        "<tr><td>1</td><td>Computer systems security</td><td>Moscow</td><td>4 years</td><td>Russian</td></tr></table>"
    )
    assert parser.programs == [{"code": "10.03.01", "programme": "Information Security", "track": "Computer systems security", "language": "Russian"}]
