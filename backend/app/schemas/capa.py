from pydantic import BaseModel, Field


class CAPARecommendation(BaseModel):
    corrective_actions: list[str] = Field(
        default_factory=list,
    )
    preventive_actions: list[str] = Field(
        default_factory=list,
    )
    rationale: str
    disclaimer: str = (
        "AI-generated CAPA guidance. "
        "CAPA actions must be reviewed, approved, "
        "and implemented by authorized QA personnel."
    )