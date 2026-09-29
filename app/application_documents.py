"""Prepare a portable, source-linked checklist for an application route."""

from .models import Application
from .admission_guides import render_admission_guide


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
        "guide": "Инструкция по подаче и оформлению договора",
        "applicant_note": "Заметка абитуриента", "program_source": "Источник программы",
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
        "guide": "Submission and contract instructions",
        "applicant_note": "Applicant note", "program_source": "Programme source",
    },
    "fr": {
        "title": "Liste de préparation à l’admission", "notice": "Cette liste est personnelle. Ce n’est ni un formulaire officiel ni une candidature déposée. Confirmez les exigences auprès de l’université avant tout envoi.",
        "programme": "Programme", "university": "Université", "cycle": "Année d’admission prévue", "tasks": "Étapes", "documents": "Documents à préparer",
        "required": "indiqué comme obligatoire", "optional": "complémentaire", "ready": "prêt", "missing": "à préparer", "review": "à vérifier",
        "description": "Note", "source": "Source officielle", "empty": "La liste des documents pour cette rentrée n’a pas été confirmée par l’université.", "guide": "Instructions de dépôt et de contrat", "applicant_note": "Note du candidat", "program_source": "Source du programme",
    },
    "es": {
        "title": "Lista de preparación para la admisión", "notice": "Esta lista es personal. No es un formulario oficial ni una solicitud presentada. Confirma los requisitos con la universidad antes de enviar documentos.",
        "programme": "Programa", "university": "Universidad", "cycle": "Año de admisión previsto", "tasks": "Pasos", "documents": "Documentos que preparar",
        "required": "indicado como obligatorio", "optional": "adicional", "ready": "listo", "missing": "pendiente", "review": "requiere revisión",
        "description": "Nota", "source": "Fuente oficial", "empty": "La universidad no ha confirmado la lista de documentos para esta convocatoria.", "guide": "Instrucciones de presentación y contrato", "applicant_note": "Nota del solicitante", "program_source": "Fuente del programa",
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
                lines.append(f"{labels['applicant_note']}: {item.comment}")
            if item.document.source_url:
                lines.append(f"{labels['source']}: {item.document.source_url}")
            lines.append("")

    lines.extend(("", labels["guide"], render_admission_guide(program.university.short_name, locale), "", f"{labels['program_source']}: {program.source_url}"))
    return ("\n".join(lines).strip() + "\n").encode("utf-8")
