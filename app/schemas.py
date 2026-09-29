from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfileUpdate(BaseModel):
    first_name: str | None = None
    country: str | None = None
    age: int | None = Field(default=None, ge=16, le=100)
    current_education: str | None = None
    graduation_year: int | None = Field(default=None, ge=2000, le=2100)
    degree: str | None = None
    field: str | None = None
    language: str | None = None
    russian_level: str | None = None
    ui_language: str = Field(default="ru", pattern="^(ru|en|fr|es)$")
    budget: float | None = Field(default=None, ge=0)
    currency: str = "RUB"
    budget_currency: str = "RUB"
    needs_dormitory: bool = False
    interested_in_quota: bool = False
    admission_year: int | None = Field(default=None, ge=2020, le=2100)


class ProfileResponse(ProfileUpdate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    max_user_id: int
    state: str
    created_at: datetime


class RecommendationRequest(BaseModel):
    user_id: int
    query: str | None = Field(default=None, max_length=200)


class Recommendation(BaseModel):
    program_id: int
    university: str
    university_short_name: str
    program: str
    language: str
    tuition: float | None
    currency: str
    dormitory: bool | None
    match_count: int
    criteria_count: int
    matched: list[str]
    not_matched: list[str]
    source_url: str


class ProgramResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    university: str
    university_short_name: str
    name: str
    degree: str
    field: str
    language: str
    duration_years: int
    tuition: float | None
    currency: str
    dormitory: bool | None
    description: str
    requirements: list[dict]
    documents: list[dict]
    deadlines: list[dict]
    source_url: str
    verified_at: date
    admission_cycle: int
    facts: list[dict] = []


class ApplicationCreate(BaseModel):
    user_id: int
    program_id: int


class StepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    step_type: str
    title: str
    description: str
    source_url: str
    deadline: date | None
    status: str
    position: int


class ApplicationResponse(BaseModel):
    id: int
    program_id: int
    program_name: str
    university: str
    status: str
    completed_steps: int
    total_steps: int
    next_step: str | None
    steps: list[StepResponse]
    documents: list["ApplicationDocumentResponse"] = []


class ApplicationDocumentUpdate(BaseModel):
    status: str = Field(pattern="^(missing|ready|needs_review)$")
    comment: str = Field(default="", max_length=1000)


class ApplicationDocumentResponse(BaseModel):
    id: int
    document_id: int
    name: str
    required: bool
    description: str
    source_url: str
    status: str
    comment: str


class QuestionRequest(BaseModel):
    user_id: int
    question: str = Field(min_length=3, max_length=1000)


class UniversityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    short_name: str
    website: str
    city: str
    description: str
    university_type: str
    study_fields: str
    tuition_min: float | None
    tuition_max: float | None
    foreign_programs: bool | None
    admissions_url: str
    catalog_level: str
    verified_at: date | None
    source_url: str


ApplicationResponse.model_rebuild()
