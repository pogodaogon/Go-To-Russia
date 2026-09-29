from types import SimpleNamespace

from app.application_documents import render_application_checklist

def test_checklist_is_utf8_and_contains_official_sources_without_private_documents():
    document = SimpleNamespace(name="Passport", required=True, description="Translate into Russian", source_url="https://university.example/admission")
    app = SimpleNamespace(
        program=SimpleNamespace(name="Information Security", university=SimpleNamespace(name="Example University", short_name="EX"), admission_cycle=2027, source_url="https://university.example/program"),
        steps=[SimpleNamespace(status="completed", position=1, title="Check requirements", description="Read the current list", source_url="https://university.example/admission")],
        documents=[SimpleNamespace(status="ready", document=document, comment="Translation requested")],
    )
    output = render_application_checklist(app, "en").decode("utf-8")
    assert "not an official form" in output
    assert "https://university.example/admission" in output
    assert "Passport" in output and "ready" in output
    assert "Translation requested" in output
    assert "document scan" not in output.lower()
