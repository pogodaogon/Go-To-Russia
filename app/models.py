from datetime import date as DateType, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    max_user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_education: Mapped[str | None] = mapped_column(String(80), nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    degree: Mapped[str | None] = mapped_column(String(40), nullable=True)
    field: Mapped[str | None] = mapped_column(String(120), nullable=True)
    language: Mapped[str | None] = mapped_column(String(40), nullable=True)
    russian_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ui_language: Mapped[str] = mapped_column(String(8), default="ru")
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget_currency: Mapped[str] = mapped_column(String(8), default="RUB")
    currency: Mapped[str] = mapped_column(String(8), default="RUB")
    needs_dormitory: Mapped[bool] = mapped_column(Boolean, default=False)
    interested_in_quota: Mapped[bool] = mapped_column(Boolean, default=False)
    admission_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    state: Mapped[str] = mapped_column(String(60), default="start")
    consent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    consent_version: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    applications: Mapped[list["Application"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class University(Base):
    __tablename__ = "universities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    short_name: Mapped[str] = mapped_column(String(80))
    website: Mapped[str] = mapped_column(String(500))
    city: Mapped[str] = mapped_column(String(80), default="Moscow")
    description: Mapped[str] = mapped_column(Text, default="")
    university_type: Mapped[str] = mapped_column(String(60), default="university")
    study_fields: Mapped[str] = mapped_column(Text, default="")
    tuition_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    tuition_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    foreign_programs: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    admissions_url: Mapped[str] = mapped_column(String(500), default="")
    catalog_level: Mapped[str] = mapped_column(String(20), default="overview")
    verified_at: Mapped[DateType | None] = mapped_column(Date, nullable=True)
    source_url: Mapped[str] = mapped_column(String(500), default="")
    programs: Mapped[list["Program"]] = relationship(back_populates="university", cascade="all, delete-orphan")


class Program(Base):
    __tablename__ = "programs"
    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"))
    name: Mapped[str] = mapped_column(String(240))
    degree: Mapped[str] = mapped_column(String(40))
    field: Mapped[str] = mapped_column(String(120))
    categories: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String(40))
    duration_years: Mapped[int] = mapped_column(Integer, default=4)
    tuition: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="RUB")
    dormitory: Mapped[bool] = mapped_column(Boolean, default=False)
    dormitory_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    admission_routes: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    source_url: Mapped[str] = mapped_column(String(500))
    verified_at: Mapped[DateType] = mapped_column(Date, default=lambda: __import__("datetime").date.today())
    admission_cycle: Mapped[int] = mapped_column(Integer, default=2027)
    listed: Mapped[bool] = mapped_column(Boolean, default=True)
    university: Mapped[University] = relationship(back_populates="programs")
    requirements: Mapped[list["Requirement"]] = relationship(back_populates="program", cascade="all, delete-orphan")
    deadlines: Mapped[list["Deadline"]] = relationship(back_populates="program", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(back_populates="program", cascade="all, delete-orphan")
    facts: Mapped[list["ProgramFact"]] = relationship(back_populates="program", cascade="all, delete-orphan")


class ProgramFact(Base):
    __tablename__ = "program_facts"
    __table_args__ = (UniqueConstraint("program_id", "key", "admission_cycle", name="uq_program_fact_cycle"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    key: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(String(500))
    verified_at: Mapped[DateType] = mapped_column(Date)
    admission_cycle: Mapped[int] = mapped_column(Integer)
    program: Mapped[Program] = relationship(back_populates="facts")


class Requirement(Base):
    __tablename__ = "requirements"
    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    type: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(String(500))
    verified_at: Mapped[DateType] = mapped_column(Date, default=lambda: __import__("datetime").date.today())
    program: Mapped[Program] = relationship(back_populates="requirements")


class Deadline(Base):
    __tablename__ = "deadlines"
    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    type: Mapped[str] = mapped_column(String(80), default="application")
    date: Mapped[DateType] = mapped_column(Date)
    admission_cycle: Mapped[int] = mapped_column(Integer, default=2027)
    source_url: Mapped[str] = mapped_column(String(500))
    verified_at: Mapped[DateType] = mapped_column(Date, default=lambda: __import__("datetime").date.today())
    program: Mapped[Program] = relationship(back_populates="deadlines")


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    name: Mapped[str] = mapped_column(String(180))
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str] = mapped_column(Text, default="")
    source_url: Mapped[str] = mapped_column(String(500))
    verified_at: Mapped[DateType | None] = mapped_column(Date, nullable=True)
    program: Mapped[Program] = relationship(back_populates="documents")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("user_id", "program_id", name="uq_user_program_application"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    status: Mapped[str] = mapped_column(String(40), default="in_progress")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped[User] = relationship(back_populates="applications")
    program: Mapped[Program] = relationship()
    steps: Mapped[list["ApplicationStep"]] = relationship(back_populates="application", cascade="all, delete-orphan", order_by="ApplicationStep.position")
    documents: Mapped[list["ApplicationDocument"]] = relationship(back_populates="application", cascade="all, delete-orphan", order_by="ApplicationDocument.id")


class ApplicationStep(Base):
    __tablename__ = "application_steps"
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    step_type: Mapped[str] = mapped_column(String(60))
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    source_url: Mapped[str] = mapped_column(String(500), default="")
    deadline: Mapped[DateType | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    position: Mapped[int] = mapped_column(Integer)
    application: Mapped[Application] = relationship(back_populates="steps")


class ApplicationDocument(Base):
    __tablename__ = "application_documents"
    __table_args__ = (UniqueConstraint("application_id", "document_id", name="uq_application_document"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    status: Mapped[str] = mapped_column(String(30), default="missing")
    comment: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    application: Mapped[Application] = relationship(back_populates="documents")
    document: Mapped[Document] = relationship()


class ReminderLog(Base):
    __tablename__ = "reminder_logs"
    __table_args__ = (UniqueConstraint("application_id", "deadline_id", "days_before", name="uq_reminder_delivery"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    deadline_id: Mapped[int] = mapped_column(ForeignKey("deadlines.id"))
    days_before: Mapped[int] = mapped_column(Integer)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProcessedUpdate(Base):
    __tablename__ = "processed_updates"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    max_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
