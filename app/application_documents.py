"""Prepare a portable, source-linked checklist for an application route."""

from .models import Application


LABELS = {
    "ru": {
        "title": "План подготовки к поступлению",
        "notice": "Это персональный чек-лист, а не официальная анкета и не поданная заявка. Перед отправкой документов проверьте требования в вузе.",
        "programme": "Программа",
        "university": "Вуз",
        "cycle": "Планируемый год поступления",
        "tasks": "Этапы",
        "documents": "Документы для подготовки",
        "required": "обязательный по каталогу",
        "optional": "дополнительный",
        "ready": "готов",
        "missing": "не готов",
        "review": "нужна проверка",
        "description": "Комментарий",
        "source": "Официальный источник",
        "empty": "Список документов пока не подтверждён вузом для этого цикла.",
    },
    "en": {
        "title": "Admission preparation checklist",
        "notice": "This is a personal checklist, not an official form or submitted application. Confirm requirements with the university before sending documents.",
        "programme": "Programme",
        "university": "University",
        "cycle": "Planned admission year",
        "tasks": "Steps",
        "documents": "Documents to prepare",
        "required": "listed as required",
        "optional": "additional",
        "ready": "ready",
        "missing": "not ready",
        "review": "needs review",
        "description": "Note",
        "source": "Official source",
        "empty": "A document list for this admission cycle has not been confirmed by the university.",
    },
}


def render_application_checklist(application: Application, locale: str = "en") -> bytes:
    labels = LABELS.get(locale, LABELS["en"])
    program = application.program
    lines = [
        labels["title"],
        "=" * len(labels["title"]),
        f"{labels['university']}: {program.university.name} ({program.university.short_name})",
        f"{labels['programme']}: {program.name}",
        f"{labels['cycle']}: {program.admission_cycle}",
        "",
        labels["notice"],
        "",
        labels["tasks"],
    ]
    for step in application.steps:
        status = labels["ready"] if step.status == "completed" else labels["missing"]
        lines.extend((f"[{status}] {step.position}. {step.title}", step.description))
        if step.source_url:
            lines.append(f"{labels['source']}: {step.source_url}")
        lines.append("")

    lines.append(labels["documents"])
    if not application.documents:
        lines.extend((labels["empty"], f"{labels['source']}: {program.source_url}"))
    else:
        for item in application.documents:
            status_key = {"ready": "ready", "needs_review": "review"}.get(item.status, "missing")
            required = labels["required"] if item.document.required else labels["optional"]
            lines.append(f"[{labels[status_key]}] {item.document.name} ({required})")
            if item.document.description:
                lines.append(f"{labels['description']}: {item.document.description}")
            if item.comment:
                lines.append(f"Applicant note: {item.comment}")
            if item.document.source_url:
                lines.append(f"{labels['source']}: {item.document.source_url}")
            lines.append("")

    lines.extend(("", f"Programme source: {program.source_url}"))
    return ("\n".join(lines).strip() + "\n").encode("utf-8")
