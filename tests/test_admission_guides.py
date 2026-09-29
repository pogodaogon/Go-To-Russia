import pytest

from app.admission_guides import GUIDES, LABELS, render_admission_guide
from app.application_documents import render_application_checklist


@pytest.mark.parametrize("university", sorted(GUIDES))
@pytest.mark.parametrize("locale", ["ru", "en", "fr", "es"])
def test_admission_guide_is_complete_and_localized(university, locale):
    guide = render_admission_guide(university, locale)
    assert guide
    assert GUIDES[university]["url"] in guide
    assert GUIDES[university]["contact_url"] in guide
    assert GUIDES[university]["steps"][locale] in guide
    assert f"{LABELS[locale]['page']}:" in guide
    assert f"{LABELS[locale]['source']}:" in guide


def test_checklist_includes_localized_guide_for_selected_university():
    from types import SimpleNamespace

    app = SimpleNamespace(
        program=SimpleNamespace(
            name="Information Security", university=SimpleNamespace(name="MTUCI", short_name="MTUCI"),
            admission_cycle=2027, source_url="https://en.mtuci.ru/academics/undergraduate_programmes/",
        ),
        steps=[], documents=[],
    )
    for locale in ("ru", "en", "fr", "es"):
        content = render_application_checklist(app, locale).decode("utf-8")
        assert GUIDES["MTUCI"]["steps"][locale] in content
        assert GUIDES["MTUCI"]["address"] in content
