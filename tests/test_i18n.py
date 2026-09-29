from types import SimpleNamespace

import pytest

from app.i18n import LANGUAGES, PROGRAM_TRANSLATIONS, ROUTE_STEPS, TEXT, programme_content, tr
from app.schemas import ProfileUpdate


def test_all_supported_locales_have_complete_ui_and_route_translations():
    keys = set(TEXT["en"])
    step_types = {step[0] for step in ROUTE_STEPS["en"]}
    for locale in LANGUAGES:
        assert set(TEXT[locale]) == keys
        assert {step[0] for step in ROUTE_STEPS[locale]} == step_types
        assert len(ROUTE_STEPS[locale]) == 7


def test_profile_accepts_supported_ui_languages_only():
    for locale in LANGUAGES:
        assert ProfileUpdate(ui_language=locale).ui_language == locale
    with pytest.raises(ValueError):
        ProfileUpdate(ui_language="de")


def test_program_details_are_translated_for_all_supported_locales():
    for locale in LANGUAGES:
        translations = (
            None
            if locale == "en"
            else PROGRAM_TRANSLATIONS["MIPT_ru"]
            if locale == "ru"
            else PROGRAM_TRANSLATIONS["MIPT"].get(locale)
        )
        assert (translations is None) == (locale == "en")
        program = SimpleNamespace(
            university=SimpleNamespace(short_name="MIPT"),
            description="English description",
            requirements=[SimpleNamespace(value="Original requirement") for _ in range(4)],
            documents=[SimpleNamespace(name="Passport", description="Original document") for _ in range(4)],
        )
        description, requirements, documents = programme_content(program, locale)
        assert description
        assert len(requirements) == 4
        assert len(documents) == 4
        assert tr(locale, "choose_language")
