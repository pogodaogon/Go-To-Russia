"""Curated catalogue data. Current-cycle prices and dates stay unknown until published."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Document, Program, ProgramFact, Requirement, University


VERIFIED_AT = date(2026, 9, 28)
CATALOG = [
    {
        "short_name": "MIPT", "university": "Moscow Institute of Physics and Technology", "website": "https://eng.mipt.ru/", "city": "Dolgoprudny",
        "admissions_url": "https://eng.mipt.ru/how-to-apply/undergraduate/", "fields": "computer science, engineering, biotechnology, applied mathematics",
        "name": "Computer Science", "degree": "bachelor", "field": "computer_science", "categories": "computer_science, artificial_intelligence, applied_mathematics, software_engineering, data_science",
        "language": "english", "duration": 4, "source": "https://eng.mipt.ru/programs/undergraduate/",
        "description": "English-taught bachelor's programme. MIPT's current catalogue lists a 2026 tuition price; tuition and dates for admission cycle 2027 are not confirmed.",
        "facts": [("tuition", "554000", "RUB", 2026, "https://eng.mipt.ru/programs/undergraduate/")],
        "requirements": [("education", "Secondary school certificate/diploma with transcript; legalization and notarized Russian translation are specified by MIPT."), ("language", "B2 English or equivalent is listed as optional for the English-taught route."), ("admission", "Confirm entrance assessment and cycle deadlines with MIPT before applying.")],
        "documents": [("Passport", "MIPT specifies legalization and notarized Russian translation.", "https://eng.mipt.ru/how-to-apply/undergraduate/"), ("School certificate and transcript", "Secondary education records with legalization and notarized Russian translation.", "https://eng.mipt.ru/how-to-apply/undergraduate/"), ("Application form", "Listed in MIPT's English-taught application checklist.", "https://eng.mipt.ru/how-to-apply/undergraduate/")],
    },
    {
        "short_name": "MIPT", "university": "Moscow Institute of Physics and Technology", "website": "https://eng.mipt.ru/", "city": "Dolgoprudny",
        "admissions_url": "https://eng.mipt.ru/how-to-apply/undergraduate/", "fields": "biotechnology, biomedical engineering, biology, engineering",
        "name": "Biomedical Engineering", "degree": "bachelor", "field": "engineering", "categories": "biomedical_engineering, biotechnology, biology, machine_learning",
        "language": "english", "duration": 4, "source": "https://eng.mipt.ru/programs/undergraduate/",
        "description": "English-taught bachelor's programme listed in MIPT's undergraduate catalogue. Confirm the 2027 intake conditions directly with MIPT.",
        "facts": [("tuition", "554000", "RUB", 2026, "https://eng.mipt.ru/programs/undergraduate/")],
        "requirements": [("education", "MIPT lists secondary school records and passport documents for international applicants; legalization and Russian translations may be required."), ("language", "The programme is listed as English-taught; confirm accepted English evidence with MIPT."), ("admission", "The programme page describes biology, chemistry and mathematics preparation; confirm entrance assessment and deadlines with MIPT.")],
        "documents": [("Passport", "Check the current legalization and translation rules with MIPT.", "https://eng.mipt.ru/how-to-apply/undergraduate/"), ("School certificate and transcript", "Secondary education records with translations and legalization where required.", "https://eng.mipt.ru/how-to-apply/undergraduate/"), ("Application form", "Listed in MIPT's international application checklist.", "https://eng.mipt.ru/how-to-apply/undergraduate/")],
    },
    {
        "short_name": "HSE", "university": "National Research University Higher School of Economics", "website": "https://www.hse.ru/en/",
        "admissions_url": "https://admissions.hse.ru/en/undergraduate-apply", "fields": "computer science, data science, economics, business, social sciences",
        "name": "Data Science and Business Analytics", "degree": "bachelor", "field": "data_science", "categories": "data_science, computer_science, artificial_intelligence, economics, business_analytics",
        "language": "english", "duration": 4, "source": "https://admissions.hse.ru/en/undergraduate-apply/scholarships_ba/",
        "description": "HSE lists this four-year, full-time programme in English. Tuition and admission dates stored here apply to the 2026 cycle only; the 2027 intake is not confirmed.",
        "facts": [("tuition", "1000000", "RUB", 2026, "https://admissions.hse.ru/en/undergraduate-apply/scholarships_ba/")],
        "requirements": [("education", "Foreign applicants submit education documents and complete HSE's credential recognition process."), ("entrance_exam", "HSE's current international admissions information lists Mathematics and English for this programme; recheck the next cycle."), ("application", "Applications are submitted through HSE's international applicant process.")],
        "documents": [("Passport", "Upload a passport scan and provide a notarized Russian translation where required.", "https://admissions.hse.ru/en/undergraduate-apply/basteps"), ("Education certificate and transcript", "Submit education documents and translations; legalization depends on issuing country.", "https://admissions.hse.ru/en/undergraduate-apply/basteps"), ("Entrance exam results", "Check the current cycle's Mathematics and English requirements.", "https://admissions.hse.ru/en/undergraduate-apply/scholarships_ba/")],
    },
    {
        "short_name": "HSE", "university": "National Research University Higher School of Economics", "website": "https://www.hse.ru/en/",
        "admissions_url": "https://admissions.hse.ru/en/undergraduate-apply", "fields": "business, economics, international relations",
        "name": "International Business", "degree": "bachelor", "field": "economics", "categories": "business, economics, international_business, management",
        "language": "english", "duration": 4, "source": "https://www.hse.ru/en/ba/ib/tracks",
        "description": "HSE describes the programme as a four-year degree taught entirely in English in Moscow. Requirements, tuition and deadlines must be checked for the chosen intake.",
        "facts": [],
        "requirements": [("language", "The programme is taught entirely in English; the programme page describes English and Mathematics entrance examinations for international applicants."), ("application", "Follow the international applicant account and credential recognition instructions for the chosen intake.")],
        "documents": [("Passport", "Follow the HSE international applicant document instructions.", "https://admissions.hse.ru/en/undergraduate-apply/basteps"), ("Education certificate and transcript", "Submit education records for HSE's credential recognition process.", "https://admissions.hse.ru/en/undergraduate-apply/basteps")],
    },
    {
        "short_name": "MAI", "university": "Moscow Aviation Institute", "website": "https://en.mai.ru/",
        "admissions_url": "https://en.mai.ru/education/international-bachelor/english-medium-programs/", "fields": "aircraft engineering, aerospace, propulsion, control systems",
        "name": "Aircraft Engineering", "degree": "bachelor", "field": "engineering", "categories": "engineering, aerospace, aircraft, mechanical_engineering",
        "language": "english", "duration": 4, "source": "https://en.mai.ru/education/international-bachelor/english-medium-programs/aircraft-engineering/",
        "description": "MAI lists this four-year, full-time English-medium bachelor's programme. The published RUB 500,000 annual fee is a 2026-cycle reference; the 2027 fee and deadlines are not confirmed.",
        "facts": [("tuition", "500000", "RUB", 2026, "https://en.mai.ru/education/tuition-fee/")],
        "requirements": [("entrance_exam", "MAI's programme page lists Mathematics and Physics entrance examinations."), ("language", "The programme page lists English as the language of instruction."), ("admission", "Confirm the next admission cycle's exact dates and document checklist with MAI.")],
        "documents": [("Passport", "See MAI's international applicant instructions.", "https://en.mai.ru/admission/faq/"), ("Education certificate and transcript", "MAI requests secondary education documents; confirm translation and legalization requirements.", "https://en.mai.ru/admission/faq/"), ("Entrance exam results", "Mathematics and Physics are listed for this programme.", "https://en.mai.ru/education/international-bachelor/english-medium-programs/aircraft-engineering/")],
    },
    {
        "short_name": "MAI", "university": "Moscow Aviation Institute", "website": "https://en.mai.ru/",
        "admissions_url": "https://en.mai.ru/education/international-bachelor/english-medium-programs/", "fields": "spacecraft, aerospace, engineering",
        "name": "Spacecraft Engineering", "degree": "bachelor", "field": "engineering", "categories": "engineering, aerospace, spacecraft, applied_physics",
        "language": "english", "duration": 4, "source": "https://en.mai.ru/education/international-bachelor/english-medium-programs/spacecraft-engineering/",
        "description": "MAI lists this four-year, full-time English-medium bachelor's programme. The published RUB 500,000 annual fee is a 2026-cycle reference; the 2027 fee and deadlines are not confirmed.",
        "facts": [("tuition", "500000", "RUB", 2026, "https://en.mai.ru/education/tuition-fee/")],
        "requirements": [("entrance_exam", "MAI's programme page lists Mathematics and Physics entrance examinations."), ("language", "The programme page lists English as the language of instruction."), ("admission", "Confirm the next admission cycle's exact dates and document checklist with MAI.")],
        "documents": [("Passport", "See MAI's international applicant instructions.", "https://en.mai.ru/admission/faq/"), ("Education certificate and transcript", "MAI requests secondary education documents; confirm translation and legalization requirements.", "https://en.mai.ru/admission/faq/"), ("Entrance exam results", "Mathematics and Physics are listed for this programme.", "https://en.mai.ru/education/international-bachelor/english-medium-programs/spacecraft-engineering/")],
    },
    {
        "short_name": "MAI", "university": "Moscow Aviation Institute", "website": "https://en.mai.ru/",
        "admissions_url": "https://en.mai.ru/education/international-bachelor/english-medium-programs/", "fields": "propulsion engineering, aerospace, mechanical engineering",
        "name": "Propulsion Engineering", "degree": "bachelor", "field": "engineering", "categories": "engineering, aerospace, propulsion, mechanical_engineering",
        "language": "english", "duration": 4, "source": "https://en.mai.ru/education/international-bachelor/english-medium-programs/propulsion-engineering/index.php",
        "description": "MAI lists this four-year, full-time English-medium bachelor's programme. The published RUB 500,000 annual fee is a 2026-cycle reference; the 2027 fee and deadlines are not confirmed.",
        "facts": [("tuition", "500000", "RUB", 2026, "https://en.mai.ru/education/tuition-fee/")],
        "requirements": [("entrance_exam", "MAI's programme page lists Mathematics and Physics entrance examinations."), ("language", "The programme page lists English as the language of instruction."), ("admission", "Confirm the next admission cycle's exact dates and document checklist with MAI.")],
        "documents": [("Passport", "See MAI's international applicant instructions.", "https://en.mai.ru/admission/faq/"), ("Education certificate and transcript", "MAI requests secondary education documents; confirm translation and legalization requirements.", "https://en.mai.ru/admission/faq/"), ("Entrance exam results", "Mathematics and Physics are listed for this programme.", "https://en.mai.ru/education/international-bachelor/english-medium-programs/propulsion-engineering/index.php")],
    },
    {
        "short_name": "MAI", "university": "Moscow Aviation Institute", "website": "https://en.mai.ru/",
        "admissions_url": "https://en.mai.ru/education/international-bachelor/english-medium-programs/", "fields": "control systems, engineering, computer science",
        "name": "Control Systems and Computer Science in Engineering", "degree": "bachelor", "field": "computer_science", "categories": "computer_science, engineering, control_systems, aerospace",
        "language": "english", "duration": 4, "source": "https://en.mai.ru/education/international-bachelor/english-medium-programs/",
        "description": "Listed by MAI among its English-medium bachelor's programmes. Verify programme-specific entrance exams, fee and 2027 intake conditions with the university.",
        "facts": [("tuition", "500000", "RUB", 2026, "https://en.mai.ru/education/tuition-fee/")],
        "requirements": [("language", "MAI lists the programme among English-medium bachelor's options."), ("admission", "Confirm the programme-specific entrance exams and next-cycle document checklist directly with MAI.")],
        "documents": [("Passport", "See MAI's international applicant instructions.", "https://en.mai.ru/admission/faq/"), ("Education certificate and transcript", "MAI requests secondary education documents; confirm translation and legalization requirements.", "https://en.mai.ru/admission/faq/")],
    },
    {
        "short_name": "Sechenov", "university": "Sechenov First Moscow State Medical University", "website": "https://www.sechenov.ru/eng/",
        "admissions_url": "https://www.sechenov.ru/eng/education-study/admission/", "fields": "medicine, dentistry, pharmacy",
        "name": "General Medicine", "degree": "specialist", "field": "medicine", "categories": "medicine, clinical_medicine, biology, chemistry",
        "language": "english", "duration": 6, "source": "https://www.sechenov.ru/eng/education-study/admission/?new=eng",
        "description": "Sechenov lists General Medicine as an English-taught six-year specialist programme for 2026/27. The 2027/28 intake details must be confirmed.",
        "facts": [], "requirements": [("entrance_exam", "The 2026/27 international admissions page lists Chemistry and Russian language exams for General Medicine; confirm requirements for the next cycle."), ("language", "The English-taught profile is listed by Sechenov; check the language and exam conditions.")],
        "documents": [("Passport", "Use Sechenov's international applicant instructions.", "https://www.sechenov.ru/eng/education-study/admission/?new=eng"), ("Education certificate and transcript", "Check current translation, recognition and legalization requirements with Sechenov.", "https://www.sechenov.ru/eng/education-study/admission/?new=eng")],
    },
    {
        "short_name": "Sechenov", "university": "Sechenov First Moscow State Medical University", "website": "https://www.sechenov.ru/eng/",
        "admissions_url": "https://www.sechenov.ru/eng/education-study/admission/", "fields": "dentistry, medicine, biology, chemistry",
        "name": "Dentistry", "degree": "specialist", "field": "medicine", "categories": "dentistry, medicine, biology, chemistry",
        "language": "english", "duration": 5, "source": "https://www.sechenov.ru/eng/education-study/admission/?new=eng",
        "description": "Sechenov lists Dentistry as an English-taught five-year specialist programme for 2026/27. The 2027/28 intake details must be confirmed.",
        "facts": [], "requirements": [("entrance_exam", "The 2026/27 international admissions page lists entrance examinations for Dentistry; confirm subjects and language for the next cycle."), ("language", "The English-taught profile is listed by Sechenov; check the language and exam conditions.")],
        "documents": [("Passport", "Use Sechenov's international applicant instructions.", "https://www.sechenov.ru/eng/education-study/admission/?new=eng"), ("Education certificate and transcript", "Check current translation, recognition and legalization requirements with Sechenov.", "https://www.sechenov.ru/eng/education-study/admission/?new=eng")],
    },
    {
        "short_name": "Sechenov", "university": "Sechenov First Moscow State Medical University", "website": "https://www.sechenov.ru/eng/",
        "admissions_url": "https://www.sechenov.ru/eng/education-study/admission/", "fields": "pharmacy, medicine, biology, chemistry",
        "name": "Pharmacy", "degree": "specialist", "field": "medicine", "categories": "pharmacy, medicine, biology, chemistry",
        "language": "english", "duration": 5, "source": "https://www.sechenov.ru/eng/education-study/admission/?new=eng",
        "description": "Sechenov lists Pharmacy as an English-taught five-year specialist programme for 2026/27. The 2027/28 intake details must be confirmed.",
        "facts": [], "requirements": [("entrance_exam", "The 2026/27 international admissions page lists Chemistry entrance examination requirements for Pharmacy; confirm the next cycle."), ("language", "The English-taught profile is listed by Sechenov; check the language and exam conditions.")],
        "documents": [("Passport", "Use Sechenov's international applicant instructions.", "https://www.sechenov.ru/eng/education-study/admission/?new=eng"), ("Education certificate and transcript", "Check current translation, recognition and legalization requirements with Sechenov.", "https://www.sechenov.ru/eng/education-study/admission/?new=eng")],
    },
    {
        "short_name": "MSU", "university": "Lomonosov Moscow State University", "website": "https://www.msu.ru/en/",
        "admissions_url": "https://fgp.msu.ru/admission/eng", "fields": "international relations, global studies, social sciences",
        "name": "International Relations and Global Studies", "degree": "bachelor", "field": "economics", "categories": "international_relations, economics, social_sciences, global_studies",
        "language": "english", "duration": 4, "source": "https://fgp.msu.ru/admission/eng",
        "description": "The Faculty of Global Studies publishes an English-language admission page and a 2026/27 contract tuition price. The next cycle's requirements and fee are not confirmed.",
        "facts": [("tuition", "586130", "RUB", 2026, "https://fgp.msu.ru/admission/eng")],
        "requirements": [("documents", "The faculty lists translated education documents and transcript among its application documents."), ("admission", "Confirm the next cycle's entrance exams, application route and deadlines with the faculty.")],
        "documents": [("Passport", "See the faculty's English-language admission checklist.", "https://fgp.msu.ru/admission/eng"), ("Education certificate and transcript", "The faculty specifies notarized Russian translations of education documents and transcript.", "https://fgp.msu.ru/admission/eng")],
    },
    {
        "short_name": "MEPhI", "university": "National Research Nuclear University MEPhI", "website": "https://eng.mephi.ru/",
        "admissions_url": "https://eng.mephi.ru/academics/admissions", "fields": "information security, cybersecurity, computer science",
        "name": "Information Security — Computer Systems Security", "degree": "bachelor", "field": "information_security",
        "categories": "information_security, cybersecurity, computer_security, computer_science",
        "language": "russian", "duration": 4, "source": "https://eng.mephi.ru/academics/degrees-and-programs/ba",
        "description": "MEPhI's official bachelor's catalogue lists Information Security (10.03.01), Computer Systems Security, taught in Russian. The 2027/28 international intake, tuition, deadlines and available places are not confirmed yet.",
        "facts": [],
        "requirements": [("language", "The official programme list identifies Russian as the language of study; confirm any Russian-language proficiency evidence required for the selected admission route."), ("admission", "MEPhI publishes admission information for international applicants. Confirm the 2027/28 programme availability, entrance exams, tuition and deadlines directly with the university.")],
        "documents": [("Passport", "Use MEPhI's current international applicant instructions; document translation and legalization requirements depend on the issuing country.", "https://eng.mephi.ru/academics/admissions"), ("Education certificate and transcript", "Confirm credential recognition, translation and legalization requirements with MEPhI for the 2027/28 cycle.", "https://eng.mephi.ru/academics/admissions")],
        "verified_at": date(2026, 9, 29),
    },
]


# Overview entries are discoverability records only. They are not eligible for
# recommendations until programme-level facts and sources are curated.
UNIVERSITY_OVERVIEW = [
    ("BMSTU", "Bauman Moscow State Technical University", "https://bmstu.ru/", "https://studyinrussia.ru/en/university-show/99/about", "Engineering, computer science, applied sciences"),
    ("MEPhI", "National Research Nuclear University MEPhI", "https://eng.mephi.ru/", "https://studyinrussia.ru/en/university-show/242/about", "Nuclear engineering, physics, computer science"),
    ("MISIS", "NUST MISIS", "https://en.misis.ru/", "https://en.misis.ru/applicants/undergraduate-programs/", "Materials science, engineering, computer science"),
    ("MGIMO", "Moscow State Institute of International Relations", "https://english.mgimo.ru/", "https://english.mgimo.ru/", "International relations, economics, law, languages"),
    ("MPEI", "National Research University MPEI", "https://international.mpei.ru/en", "https://international.mpei.ru/en", "Power engineering, electrical engineering, computer science"),
    ("RANEPA", "Russian Presidential Academy of National Economy and Public Administration", "https://www.ranepa.ru/eng/", "https://www.ranepa.ru/eng/higher-education/", "Economics, management, public administration"),
    ("FA", "Financial University under the Government of the Russian Federation", "https://www.fa.ru/", "https://studyinrussia.ru/en/university-show/555/about", "Finance, economics, business, information technology"),
    ("REU", "Plekhanov Russian University of Economics", "https://www.rea.ru/en/", "https://studyinrussia.ru/en/university-show/368/about", "Economics, business, management, information technology"),
    ("MGSU", "National Research Moscow State University of Civil Engineering", "https://mgsu.ru/en/", "https://studyinrussia.ru/en/university-show/481/about", "Civil engineering, architecture, construction"),
    ("MIREA", "MIREA — Russian Technological University", "https://english.mirea.ru/", "https://english.mirea.ru/", "Information technology, engineering, chemistry"),
    ("MOSPOLY", "Moscow Polytechnic University", "https://mospolytech.ru/en/", "https://studyinrussia.ru/en/university-show/228/about", "Engineering, transport, information technology"),
    ("STANKIN", "Moscow State Technological University STANKIN", "https://en.stankin.ru/", "https://en.stankin.ru/", "Mechanical engineering, robotics, automation"),
    ("MSLU", "Moscow State Linguistic University", "https://linguanet.ru/", "https://studyinrussia.ru/en/university-show/472/about", "Languages, translation, international relations"),
    ("GUBKIN", "Gubkin Russian State University of Oil and Gas", "https://en.gubkin.ru/", "https://studyinrussia.ru/en/university-show/231/about", "Oil and gas engineering, geology, energy"),
    ("RUT", "Russian University of Transport", "https://rut-miit.ru/", "https://studyinrussia.ru/en/university-show/366/about", "Transport, logistics, engineering, information technology"),
    ("GUZ", "State University of Land Management", "https://guz.ru/", "https://studyinrussia.ru/en/university-show/438/about", "Land management, geodesy, architecture"),
    ("MTUCI", "Moscow Technical University of Communications and Informatics", "https://mtuci.ru/", "https://studyinrussia.ru/en/university-show/109/about", "Telecommunications, computer science, information security"),
    ("MIET", "National Research University of Electronic Technology", "https://eng.miet.ru/", "https://eng.miet.ru/", "Electronics, computer engineering, materials science"),
    ("KOSYGIN", "A.N. Kosygin Russian State University", "https://rguk.ru/", "https://studyinrussia.ru/en/university-show/360/about", "Design, technology, arts, textiles"),
    ("PUSHKIN", "Pushkin State Russian Language Institute", "https://www.pushkin.institute/", "https://studyinrussia.ru/en/university-show/290/about", "Russian language, linguistics, philology"),
    ("RSUTS", "Russian State University of Social Technologies", "https://rsu.ru/", "https://studyinrussia.ru/en/university-show/109/about", "Social sciences, technology, rehabilitation"),
    ("MSAL", "Kutafin Moscow State Law University", "https://msal.ru/en/", "https://msal.ru/content/abiturientam/priemnaya-kampaniya/inostrannym-postupayushchim/", "Law, jurisprudence, public policy"),
    ("RSUH", "Russian State University for the Humanities", "https://rsuh.ru/en/", "https://rsuh.ru/en/", "Humanities, history, social sciences, information systems"),
    ("GUU", "State University of Management", "https://www.guu.ru/", "https://www.guu.ru/", "Management, economics, business informatics"),
    ("TIMIRYAZEV", "Russian State Agrarian University — Timiryazev Agricultural Academy", "https://www.timacad.ru/", "https://www.timacad.ru/", "Agriculture, biology, food science, engineering"),
]


def seed_database(db: Session) -> int:
    db.query(Program).update({Program.listed: False}, synchronize_session=False)
    for item in CATALOG:
        university = db.scalar(select(University).where(University.short_name == item["short_name"]))
        if university is None:
            university = University(name=item["university"], short_name=item["short_name"], website=item["website"], city="Moscow")
            db.add(university)
            db.flush()
        university.name = item["university"]
        university.website = item["website"]
        university.source_url = item["website"]
        university.city = item.get("city", "Moscow")
        university.admissions_url = item["admissions_url"]
        university.study_fields = item["fields"]
        university.foreign_programs = True
        university.catalog_level = "detailed"
        university.verified_at = VERIFIED_AT
        program = db.scalar(select(Program).where(Program.university_id == university.id, Program.name == item["name"]))
        if program is None:
            program = Program(university_id=university.id, name=item["name"], degree=item["degree"], field=item["field"], language=item["language"], duration_years=item["duration"], source_url=item["source"], verified_at=VERIFIED_AT, admission_cycle=2027)
            db.add(program)
            db.flush()
        program.degree = item["degree"]
        program.field = item["field"]
        program.categories = item["categories"]
        program.language = item["language"]
        program.duration_years = item["duration"]
        program.tuition = None
        program.currency = "RUB"
        program.source_url = item["source"]
        program.description = item["description"]
        program.admission_cycle = 2027
        program.dormitory = False
        program.dormitory_confirmed = False
        program.admission_routes = "For the 2027 cycle, contract and government quota availability must be confirmed with the university."
        program.listed = True
        program.verified_at = item.get("verified_at", VERIFIED_AT)
        db.flush()

        for kind, value in item["requirements"]:
            source = item["source"]
            record = db.scalar(select(Requirement).where(Requirement.program_id == program.id, Requirement.type == kind, Requirement.value == value))
            if record is None:
                db.add(Requirement(program_id=program.id, type=kind, value=value, source_url=source, verified_at=VERIFIED_AT))
            else:
                record.source_url = source
                record.verified_at = VERIFIED_AT

        for name, description, source in item["documents"]:
            document = db.scalar(select(Document).where(Document.program_id == program.id, Document.name == name))
            if document is None:
                db.add(Document(program_id=program.id, name=name, required=True, description=description, source_url=source, verified_at=VERIFIED_AT))
            else:
                document.description = description
                document.source_url = source
                document.verified_at = VERIFIED_AT

        for key, value, currency, cycle, source in item["facts"]:
            fact = db.scalar(select(ProgramFact).where(ProgramFact.program_id == program.id, ProgramFact.key == key, ProgramFact.admission_cycle == cycle))
            if fact is None:
                db.add(ProgramFact(program_id=program.id, key=key, value=f"{value} {currency}", source_url=source, verified_at=VERIFIED_AT, admission_cycle=cycle))
            else:
                fact.value = f"{value} {currency}"
                fact.source_url = source
    for code, name, website, source, fields in UNIVERSITY_OVERVIEW:
        university = db.scalar(select(University).where(University.short_name == code))
        if university is None:
            university = University(name=name, short_name=code, website=website, city="Moscow")
            db.add(university)
            db.flush()
        university.name = name
        university.website = website
        university.source_url = source
        university.admissions_url = source
        university.study_fields = fields
        university.catalog_level = "overview"
        university.foreign_programs = None
        university.tuition_min = None
        university.tuition_max = None
    db.flush()
    db.commit()
    return len(CATALOG)
