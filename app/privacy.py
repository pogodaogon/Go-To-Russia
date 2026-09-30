"""Privacy notice and consent copy for the applicant profile data the bot stores."""

from __future__ import annotations

from html import escape


NOTICE_VERSION = "2026-09-30-v1"
INACTIVE_RETENTION_DAYS = 365

CONSENT_COPY = {
    "ru": (
        "Перед началом прочитайте уведомление об обработке данных: {url}\n"
        "Для подбора и маршрута бот сохраняет ваш ID и имя MAX, а также ответы о стране, возрасте, образовании, направлении, языке, бюджете, общежитии, квоте и поступлении."
        " Данные хранятся в базе проекта; документы и сканы бот не запрашивает. Вузы не получают ваш профиль."
        " Если включена внешняя языковая модель, ей может быть передан текст вашего вопроса вместе с фактами из каталога. Не включайте в вопрос паспортные и другие личные данные.\n"
        "Согласие добровольное. Удалить профиль и маршрут можно командой /delete_data; при отказе сохранённые данные будут удалены."
    ),
    "en": (
        "Before continuing, read the privacy notice: {url}\n"
        "For programme matching and your application route, the bot stores your MAX user ID and name plus your answers about country, age, education, field, language, budget, dormitory, quota and intake year."
        " Data stays in the project database; the bot does not request document scans. Universities do not receive your profile."
        " If an external language model is enabled, your question and catalogue facts may be sent to that provider. Do not include passport or other personal details in questions.\n"
        "Consent is optional. Use /delete_data to erase your profile and routes; declining also deletes saved data."
    ),
    "fr": (
        "Avant de continuer, consultez la notice de confidentialité : {url}\n"
        "Pour proposer des programmes et créer votre parcours, le bot conserve votre identifiant et votre nom MAX, ainsi que vos réponses sur le pays, l’âge, les études, le domaine, la langue, le budget, le logement, le quota et l’année d’admission."
        " Les données restent dans la base du projet ; le bot ne demande pas de scans de documents. Les universités ne reçoivent pas votre profil."
        " Si un modèle linguistique externe est activé, votre question et des faits du catalogue peuvent lui être transmis. N’incluez pas de données de passeport ou autres données personnelles dans vos questions.\n"
        "Le consentement est facultatif. Utilisez /delete_data pour supprimer votre profil et vos parcours ; un refus supprime également les données enregistrées."
    ),
    "es": (
        "Antes de continuar, lea el aviso de privacidad: {url}\n"
        "Para recomendar programas y crear su itinerario, el bot guarda su ID y nombre de MAX, además de sus respuestas sobre país, edad, estudios, área, idioma, presupuesto, residencia, cuota y año de ingreso."
        " Los datos permanecen en la base del proyecto; el bot no solicita copias de documentos. Las universidades no reciben su perfil."
        " Si se activa un modelo lingüístico externo, su pregunta y datos del catálogo pueden enviarse a ese proveedor. No incluya datos del pasaporte u otros datos personales en sus preguntas.\n"
        "El consentimiento es opcional. Use /delete_data para borrar su perfil y sus itinerarios; si lo rechaza, también se borrarán los datos guardados."
    ),
}

CONSENT_BUTTONS = {
    "ru": ("Согласен — Русский", "Не согласен — Русский"),
    "en": ("Agree — English", "Decline — English"),
    "fr": ("J’accepte — Français", "Je refuse — Français"),
    "es": ("Acepto — Español", "No acepto — Español"),
}

DECLINED = {
    "ru": "Профиль не создан. Если у вас уже были данные, они удалены. Вы можете вернуться командой /start.",
    "en": "No profile was created. Any previously saved data has been deleted. You can return with /start.",
    "fr": "Aucun profil n’a été créé. Les données déjà enregistrées ont été supprimées. Vous pouvez revenir avec /start.",
    "es": "No se creó ningún perfil. Los datos guardados anteriormente se han eliminado. Puede volver con /start.",
}

POLICY = {
    "ru": {
        "title": "Уведомление о конфиденциальности UniRoute Russia",
        "intro": "Кто обрабатывает данные",
        "controller": "Оператор",
        "contact": "Контакт для вопросов и запросов на удаление",
        "what": "Какие данные и зачем",
        "what_text": "Идентификатор и имя MAX, страна, возраст, образование, направление, язык, бюджет, предпочтения по общежитию и квоте, год поступления, выбранные программы, статусы шагов и документов. Эти данные используются только для подбора программ, показа маршрута и напоминаний.",
        "where": "Получатели и хранение",
        "where_text": "Данные хранятся в базе приложения и не передаются университетам. MAX обрабатывает сообщения как платформа. Если оператор включит внешнюю LLM, текст вопроса и факты каталога передаются её провайдеру; не отправляйте в вопросах личные данные. Документы и сканы не собираются.",
        "term": "Срок хранения и удаление",
        "term_text": "Профиль удаляется по команде /delete_data или после 365 дней бездействия. Удаление включает профиль, маршруты, статусы документов и связанные технические записи. Отказ от согласия также удаляет профиль.",
        "rights": "Ваш выбор",
        "rights_text": "Согласие добровольное. Без него подбор не работает. Вы можете отозвать его командой /delete_data или обратиться к оператору по указанному контакту.",
        "updated": "Версия уведомления",
    },
    "en": {
        "title": "UniRoute Russia privacy notice",
        "intro": "Who processes the data",
        "controller": "Controller",
        "contact": "Privacy and deletion contact",
        "what": "Data and purpose",
        "what_text": "MAX user ID and name; country, age, education, field, language, budget, dormitory and quota preferences, intake year, chosen programmes, route steps and document statuses. The app uses these data only to match programmes, show a route and send reminders.",
        "where": "Recipients and storage",
        "where_text": "Data is stored in the application database and is not sent to universities. MAX processes messages as the messaging platform. If the operator enables an external LLM, the question text and catalogue facts are sent to that provider; do not put personal data in questions. The bot does not collect document scans.",
        "term": "Retention and deletion",
        "term_text": "The profile is deleted with /delete_data or after 365 days without activity. Deletion includes the profile, routes, document statuses and linked technical records. Declining consent also deletes the profile.",
        "rights": "Your choice",
        "rights_text": "Consent is optional; matching will not work without it. Withdraw consent with /delete_data or contact the controller at the address above.",
        "updated": "Notice version",
    },
    "fr": {
        "title": "Notice de confidentialité UniRoute Russia",
        "intro": "Responsable du traitement",
        "controller": "Responsable",
        "contact": "Contact pour la confidentialité et la suppression",
        "what": "Données et finalité",
        "what_text": "Identifiant et nom MAX ; pays, âge, études, domaine, langue, budget, préférences de logement et de quota, année d’admission, programmes choisis, étapes du parcours et statuts des documents. Ces données servent uniquement à proposer des programmes, afficher un parcours et envoyer des rappels.",
        "where": "Destinataires et stockage",
        "where_text": "Les données sont stockées dans la base de l’application et ne sont pas transmises aux universités. MAX traite les messages en tant que plateforme. Si le responsable active un modèle linguistique externe, le texte de la question et des faits du catalogue lui sont transmis ; n’incluez pas de données personnelles dans vos questions. Le bot ne collecte pas de scans.",
        "term": "Conservation et suppression",
        "term_text": "Le profil est supprimé avec /delete_data ou après 365 jours d’inactivité. La suppression inclut le profil, les parcours, les statuts des documents et les données techniques associées. Le refus du consentement supprime également le profil.",
        "rights": "Votre choix",
        "rights_text": "Le consentement est facultatif ; sans lui, la recherche ne fonctionne pas. Retirez-le avec /delete_data ou contactez le responsable à l’adresse ci-dessus.",
        "updated": "Version de la notice",
    },
    "es": {
        "title": "Aviso de privacidad de UniRoute Russia",
        "intro": "Quién trata los datos",
        "controller": "Responsable",
        "contact": "Contacto de privacidad y eliminación",
        "what": "Datos y finalidad",
        "what_text": "ID y nombre de MAX; país, edad, estudios, área, idioma, presupuesto, preferencias de residencia y cuota, año de ingreso, programas elegidos, pasos del itinerario y estados de documentos. La aplicación usa estos datos solo para recomendar programas, mostrar un itinerario y enviar recordatorios.",
        "where": "Destinatarios y almacenamiento",
        "where_text": "Los datos se guardan en la base de la aplicación y no se envían a las universidades. MAX procesa los mensajes como plataforma. Si el responsable activa un modelo lingüístico externo, se envían a ese proveedor el texto de la pregunta y datos del catálogo; no incluya datos personales en sus preguntas. El bot no recopila documentos escaneados.",
        "term": "Conservación y eliminación",
        "term_text": "El perfil se elimina con /delete_data o tras 365 días de inactividad. La eliminación incluye el perfil, itinerarios, estados de documentos y registros técnicos vinculados. Rechazar el consentimiento también elimina el perfil.",
        "rights": "Su elección",
        "rights_text": "El consentimiento es opcional; sin él no funciona la búsqueda. Retírelo con /delete_data o contacte con el responsable en la dirección indicada.",
        "updated": "Versión del aviso",
    },
}


def consent_buttons() -> list[list[dict[str, str]]]:
    return [[{"type": "message", "text": label}] for lang in ("ru", "en", "fr", "es") for label in CONSENT_BUTTONS[lang]]


def consent_choice(text: str | None) -> tuple[str, bool] | None:
    if not text:
        return None
    normalized = text.strip().casefold()
    for lang, (accept, decline) in CONSENT_BUTTONS.items():
        if normalized == accept.casefold():
            return lang, True
        if normalized == decline.casefold():
            return lang, False
    return None


def consent_text(policy_url: str) -> str:
    return "\n\n".join(CONSENT_COPY[lang].format(url=f"{policy_url}?lang={lang}") for lang in ("ru", "en", "fr", "es"))


def render_policy(locale: str, controller: str, contact: str) -> str:
    lang = locale if locale in POLICY else "en"
    text = POLICY[lang]
    e = escape
    return f"""<!doctype html><html lang=\"{lang}\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{e(text['title'])}</title>
<style>body{{font:16px/1.55 system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;color:#18202b}}h1{{line-height:1.2}}h2{{margin-top:1.6rem}}li{{margin:.35rem 0}}</style><main><h1>{e(text['title'])}</h1>
<h2>{e(text['intro'])}</h2><p><b>{e(text['controller'])}:</b> {e(controller)}</p><p><b>{e(text['contact'])}:</b> {e(contact)}</p>
<h2>{e(text['what'])}</h2><p>{e(text['what_text'])}</p><h2>{e(text['where'])}</h2><p>{e(text['where_text'])}</p>
<h2>{e(text['term'])}</h2><p>{e(text['term_text'])}</p><h2>{e(text['rights'])}</h2><p>{e(text['rights_text'])}</p>
<p><b>{e(text['updated'])}:</b> {NOTICE_VERSION}</p></main></html>"""
