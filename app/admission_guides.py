"""Localized, source-linked guidance for the currently curated universities.

These are navigation instructions, not legal or admission decisions. Cycle-specific
deadlines and final contract instructions must always come from the university.
"""

LABELS = {
    "ru": {"title": "Как подать документы", "steps": "Порядок действий", "contract": "Как оформить договор", "visit": "Личный визит", "contact": "Связаться с вузом", "cycle": "Порядок и сроки следующего набора могут измениться. Перед отправкой документов проверьте страницу выбранного года и уточните детали у вуза.", "no_visit": "На официальной странице не удалось подтвердить отдельный адрес приёмной для этого действия. Сначала напишите или позвоните в вуз и уточните, куда и когда приходить.", "verify": "Перед подписанием сверьте ФИО, программу, форму обучения, сумму, сроки оплаты и условия возврата. Подписывайте и оплачивайте только по инструкциям и реквизитам из официального кабинета или от приёмной комиссии.", "page": "Официальная страница", "source": "Контакты и источник"},
    "en": {"title": "How to submit your documents", "steps": "Steps", "contract": "How to arrange the tuition contract", "visit": "In-person visit", "contact": "Contact the university", "cycle": "The next intake procedure and dates may change. Check the page for your admission year and confirm details with the university before submitting documents.", "no_visit": "We could not confirm a dedicated admissions-office address for this action on the official page. Email or call first to ask where and when to visit.", "verify": "Before signing, check your full name, programme, study mode, tuition amount, payment dates, and refund terms. Sign and pay only as instructed in the official account or by the admissions office.", "page": "Official page", "source": "Contact and source"},
    "fr": {"title": "Comment déposer votre dossier", "steps": "Étapes", "contract": "Comment établir le contrat de formation", "visit": "Visite en personne", "contact": "Contacter l’université", "cycle": "La procédure et les dates de la prochaine rentrée peuvent changer. Consultez la page correspondant à votre année d’admission et confirmez les détails auprès de l’université avant l’envoi du dossier.", "no_visit": "L’adresse d’un bureau d’admission dédié à cette démarche n’a pas pu être confirmée sur la page officielle. Écrivez ou appelez d’abord pour demander où et quand vous présenter.", "verify": "Avant de signer, vérifiez votre nom complet, le programme, le régime d’études, le montant des frais, les échéances de paiement et les conditions de remboursement. Signez et payez uniquement selon les instructions du compte officiel ou du service des admissions.", "page": "Page officielle", "source": "Contact et source"},
    "es": {"title": "Cómo presentar los documentos", "steps": "Pasos", "contract": "Cómo formalizar el contrato de estudios", "visit": "Visita presencial", "contact": "Contactar con la universidad", "cycle": "El procedimiento y las fechas de la próxima convocatoria pueden cambiar. Consulta la página del año de admisión correspondiente y confirma los detalles con la universidad antes de enviar los documentos.", "no_visit": "No hemos podido confirmar en la página oficial una dirección específica de admisiones para este trámite. Escribe o llama primero para preguntar dónde y cuándo acudir.", "verify": "Antes de firmar, comprueba tu nombre completo, programa, modalidad de estudios, importe, fechas de pago y condiciones de reembolso. Firma y paga únicamente según las instrucciones de la cuenta oficial o de admisiones.", "page": "Página oficial", "source": "Contacto y fuente"},
}

_COMMON = {
    "ru": {"contract": "Договор обычно оформляют после рассмотрения заявки или рекомендации к зачислению. Не заполняйте и не подписывайте сторонний шаблон: дождитесь проекта договора и инструкции именно для вашей программы и набора.", "visit_prefix": "Адрес, опубликованный вузом:", "contact_prefix": "Официальный контакт:"},
    "en": {"contract": "The contract is usually prepared after the application has been reviewed or admission has been recommended. Do not use or sign a third-party template: wait for the draft and instructions for your programme and intake.", "visit_prefix": "University-published address:", "contact_prefix": "Official contact:"},
    "fr": {"contract": "Le contrat est généralement préparé après l’examen du dossier ou une recommandation d’admission. N’utilisez pas et ne signez pas de modèle tiers : attendez le projet de contrat et les instructions correspondant à votre programme et à votre rentrée.", "visit_prefix": "Adresse publiée par l’université :", "contact_prefix": "Contact officiel :"},
    "es": {"contract": "El contrato suele prepararse después de revisar la solicitud o recomendar la admisión. No uses ni firmes plantillas de terceros: espera el borrador y las instrucciones de tu programa y convocatoria.", "visit_prefix": "Dirección publicada por la universidad:", "contact_prefix": "Contacto oficial:"},
}

GUIDES = {
    "MIPT": {
        "url": "https://eng.mipt.ru/how-to-apply/undergraduate/",
        "contact_url": "https://eng.mipt.ru/",
        "address": "9 Institutskiy per., Dolgoprudny, Moscow Region, 141700, Russian Federation",
        "contact": "International Admissions: interadmission@phystech.edu; +7 (498) 713-91-70",
        "steps": {
            "ru": "Откройте официальную страницу бакалавриата, выберите программу и язык обучения, затем следуйте шагам подачи и списку документов. Для договора и платёжных реквизитов обратитесь в Международную приёмную комиссию: interadmission@phystech.edu.",
            "en": "Open the official undergraduate admissions page, choose the programme and language, then follow its application steps and document list. Ask International Admissions for the contract and payment instructions: interadmission@phystech.edu.",
            "fr": "Ouvrez la page officielle des admissions en licence, choisissez le programme et la langue, puis suivez les étapes et la liste des pièces. Demandez le contrat et les instructions de paiement au service des admissions internationales : interadmission@phystech.edu.",
            "es": "Abre la página oficial de admisión de grado, elige el programa y el idioma y sigue los pasos y la lista de documentos. Solicita el contrato y las instrucciones de pago a Admisiones Internacionales: interadmission@phystech.edu.",
        },
    },
    "HSE": {
        "url": "https://admissions.hse.ru/en/contract_trajectory",
        "contact_url": "https://admissions.hse.ru/en/contract_trajectory",
        "address": "11 Pokrovsky Boulevard, Moscow, office D623 (confirm current reception arrangements before travelling)",
        "contact": "inter@hse.ru; +7 (495) 531-00-59",
        "steps": {
            "ru": "Подайте заявку через личный кабинет иностранного абитуриента. После допуска откройте раздел My Contracts, запросите проект, проверьте данные, подпишите и отправьте скан по адресу, указанному в инструкции кабинета. Срок оплаты и адрес электронной почты могут зависеть от набора — используйте актуальную инструкцию ВШЭ.",
            "en": "Apply through the foreign applicant account. Once eligible, open “My Contracts”, request the draft, check your details, sign it, and email the scan as instructed in your account. The payment deadline and email may change by intake; follow HSE’s current instructions.",
            "fr": "Déposez votre candidature dans le compte des candidats étrangers. Après confirmation de votre admissibilité, ouvrez « My Contracts », demandez le projet, vérifiez vos données, signez-le et envoyez le scan selon les instructions du compte. L’échéance et l’adresse électronique peuvent changer selon la rentrée ; suivez les consignes HSE à jour.",
            "es": "Presenta la solicitud en la cuenta para candidatos extranjeros. Cuando cumplas los requisitos, abre «My Contracts», solicita el borrador, revisa tus datos, fírmalo y envía el escaneo según las instrucciones de tu cuenta. El plazo y el correo pueden variar por convocatoria; sigue las indicaciones vigentes de HSE.",
        },
    },
    "MAI": {
        "url": "https://en.mai.ru/admission/",
        "contact_url": "https://en.mai.ru/about/int/",
        "address": "4 Dubosekovskaya Street, Main Academic Building, admissions hall, room 15 (confirm reception hours first)",
        "contact": "English-program admissions: admission@mai.ru; +7 925 579-75-89",
        "steps": {
            "ru": "Подайте документы одним из способов, указанных на официальной странице: по электронной почте, через личный кабинет или лично. После рассмотрения заявки запросите у приёмной комиссии проект договора и платёжную инструкцию; не используйте старые суммы и сроки из прошлых наборов.",
            "en": "Submit documents using one of the methods on the official page: email, applicant account, or in person. After your application is reviewed, ask Admissions for the contract draft and payment instructions. Do not rely on fees or dates from earlier intakes.",
            "fr": "Déposez les pièces selon l’une des méthodes indiquées sur la page officielle : par e-mail, via le compte candidat ou en personne. Après examen du dossier, demandez au service des admissions le projet de contrat et les instructions de paiement. Ne vous fiez pas aux tarifs ou dates d’anciennes rentrées.",
            "es": "Presenta los documentos por uno de los métodos de la página oficial: correo electrónico, cuenta del solicitante o en persona. Cuando revisen tu solicitud, pide a Admisiones el borrador del contrato y las instrucciones de pago. No uses precios ni fechas de convocatorias anteriores.",
        },
    },
    "Sechenov": {
        "url": "https://www.sechenov.ru/eng/education-study/admission/?new=eng",
        "contact_url": "https://www.sechenov.ru/eng/education-study/",
        "address": "8 Trubetskaya Street, Moscow (official Admissions Committee address; confirm the correct office and appointment before travelling)",
        "contact": "Admissions Committee: admission@staff.sechenov.ru; +7 (495) 622-98-20",
        "steps": {
            "ru": "Выберите программу и отправьте документы способом, доступным для вашего случая: ruID/личный кабинет, почтой или лично. Для платного обучения запросите договор и получите его в личном кабинете, затем подпишите и оплатите по официальной инструкции. Перед визитом уточните нужный корпус и запись у приёмной комиссии.",
            "en": "Choose a programme and submit documents using the method available to you: ruID/applicant account, post, or in person. For fee-paying study, request the contract in your applicant account, then sign and pay according to the official instructions. Confirm the correct building and appointment with Admissions before visiting.",
            "fr": "Choisissez un programme et déposez les pièces par la méthode disponible : ruID/compte candidat, courrier ou en personne. Pour une formation payante, demandez le contrat dans votre compte candidat, puis signez et payez selon les instructions officielles. Avant de vous déplacer, confirmez le bâtiment et le rendez-vous auprès des admissions.",
            "es": "Elige un programa y presenta los documentos por el método disponible: ruID/cuenta del solicitante, correo postal o en persona. Para estudios de pago, solicita el contrato en tu cuenta, y luego fírmalo y paga según las instrucciones oficiales. Confirma el edificio y la cita con Admisiones antes de acudir.",
        },
    },
    "MSU": {
        "url": "https://fgp.msu.ru/admission/eng",
        "contact_url": "https://fgp.msu.ru/about/contact",
        "address": "Leninskie Gory 1, building 13A (Building B, Faculty of Global Studies), Moscow",
        "contact": "Faculty Admissions: admission@fgp.msu.ru; +7 (495) 939-45-06",
        "steps": {
            "ru": "Это инструкция факультета глобальных процессов МГУ. Подайте заявку через webanketa.msu.ru или другим способом, опубликованным факультетом для вашего набора. По договору, комплекту оригиналов и времени личного приёма получите подтверждение у приёмной комиссии: порядок может различаться по категориям абитуриентов.",
            "en": "This guide is for MSU’s Faculty of Global Studies. Apply through webanketa.msu.ru or another method published by the faculty for your intake. Confirm the contract process, original documents, and in-person reception time with Admissions; the procedure can differ by applicant category.",
            "fr": "Ces consignes concernent la Faculté des études globales de l’Université d’État de Moscou. Déposez votre candidature sur webanketa.msu.ru ou par toute autre méthode publiée par la faculté pour votre rentrée. Confirmez auprès des admissions la procédure de contrat, les originaux et les horaires d’accueil ; la procédure dépend de la catégorie de candidat.",
            "es": "Estas instrucciones corresponden a la Facultad de Estudios Globales de la Universidad Estatal de Moscú. Solicita plaza en webanketa.msu.ru o por otro método publicado por la facultad para tu convocatoria. Confirma con Admisiones el contrato, los documentos originales y el horario presencial; el procedimiento depende de la categoría del candidato.",
        },
    },
    "MEPhI": {
        "url": "https://eng.mephi.ru/academics/admissions/tuition-fee",
        "contact_url": "https://eng.mephi.ru/admissions/contact-the-admissions",
        "address": "31 Kashirskoe Highway, Moscow, 115409 (confirm visit arrangements with the admissions coordinator)",
        "contact": "Acceptance coordinator: ONPetukhova@mephi.ru; +7 (495) 788-56-99, ext. 8045",
        "steps": {
            "ru": "Откройте официальную страницу платного приёма для выбранной программы и цикла, подайте заявку и документы в указанном формате. Уточните у координатора приёма порядок получения и подписания договора, актуальную сумму и реквизиты; не переводите деньги до получения официального договора/счёта.",
            "en": "Open the official fee-paying admissions page for your programme and intake, then submit the application and documents in the stated format. Ask the admissions coordinator how to receive and sign the contract and confirm the current fee and payment details. Do not transfer money before receiving an official contract/invoice.",
            "fr": "Consultez la page officielle des admissions payantes correspondant à votre programme et à votre rentrée, puis déposez le dossier au format indiqué. Demandez au coordinateur comment recevoir et signer le contrat et confirmez les frais et coordonnées de paiement actuels. N’effectuez aucun virement avant d’avoir reçu un contrat/une facture officiel(le).",
            "es": "Abre la página oficial de admisión con pago para tu programa y convocatoria, y presenta la solicitud y los documentos en el formato indicado. Pregunta al coordinador cómo recibir y firmar el contrato y confirma el precio y los datos de pago vigentes. No transfieras dinero antes de recibir un contrato/factura oficial.",
        },
    },
    "MTUCI": {
        "url": "https://en.mtuci.ru/education/intern_edu/",
        "contact_url": "https://en.mtuci.ru/education/intern_edu/",
        "address": "8A Aviamotornaya Street, 3rd floor, office 345, Moscow, 111024",
        "contact": "Department for Foreign Students Affairs: indec@mtuci.ru; +7 (495) 957-79-95, ext. 437/190/191",
        "steps": {
            "ru": "На странице для иностранных граждан выберите нужный уровень и программу, сверьте актуальный список документов и свяжитесь с Отделом по работе с иностранными студентами. Этот отдел оформляет договоры платного обучения. Попросите подтвердить способ подачи, список оригиналов, проект договора и реквизиты до поездки в вуз.",
            "en": "On the international applicants page, select your level and programme, check the current document list, and contact the Department for Foreign Students Affairs. This department handles tuition contracts. Ask it to confirm the submission method, original documents, contract draft, and payment details before travelling to campus.",
            "fr": "Sur la page des candidats étrangers, choisissez le niveau et le programme, vérifiez la liste actuelle des pièces et contactez le service des étudiants étrangers. Ce service gère les contrats de formation payante. Demandez-lui de confirmer le mode de dépôt, les originaux, le projet de contrat et les coordonnées de paiement avant de vous rendre sur le campus.",
            "es": "En la página para solicitantes internacionales, elige nivel y programa, revisa la lista actual de documentos y contacta con el Departamento de Estudiantes Extranjeros. Este departamento gestiona los contratos de estudios de pago. Antes de ir al campus, confirma con ellos el método de presentación, los originales, el borrador y los datos de pago.",
        },
    },
}


def render_admission_guide(short_name: str, locale: str = "en") -> str:
    guide = GUIDES.get(short_name)
    if not guide:
        return ""
    locale = locale if locale in LABELS else "en"
    labels = LABELS[locale]
    common = _COMMON[locale]
    visit = f"{common['visit_prefix']} {guide['address']}" if guide.get("address") else labels["no_visit"]
    return "\n".join((
        labels["title"],
        f"{labels['steps']}: {guide['steps'][locale]}",
        f"{labels['contract']}: {common['contract']}",
        labels["verify"],
        f"{labels['visit']}: {visit}",
        f"{labels['contact']}: {guide['contact']}",
        f"{labels['cycle']}",
        f"{labels['page']}: {guide['url']}",
        f"{labels['source']}: {guide['contact_url']}",
    ))
