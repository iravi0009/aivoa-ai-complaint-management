import json
import re

from groq import Groq

from app.core.config import settings
from app.schemas.complaint import AIComplaintExtraction


client = Groq(
    api_key=settings.groq_api_key,
)


# ============================================================
# COMPLAINT EXTRACTION
# ============================================================

SYSTEM_PROMPT = """
You are an AI assistant for a pharmaceutical customer complaint
management system.

Your task is to extract structured complaint information from
customer emails, complaint documents, or free-form text.

Do not invent information.

If a field is not available, return null.

Return ONLY valid JSON.

Required JSON structure:

{
  "complaint_source": null,
  "customer_name": null,
  "product_name": null,
  "product_strength": null,
  "batch_number": null,
  "manufacturing_date": null,
  "expiry_date": null,
  "quantity_affected": null,
  "quantity_unit": null,
  "complaint_type": null,
  "complaint_date": null,
  "description": null
}

Date format must be YYYY-MM-DD when the date is available.

Complaint type should preferably be one of:
Product Quality,
Packaging,
Labeling,
Adverse Event,
Delivery,
Documentation,
Other.
"""


def _extract_json(text: str) -> dict:
    """
    Convert the model response into a Python dictionary.

    Handles responses where the model accidentally wraps
    JSON inside markdown code fences.
    """

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        match = re.search(
            r"\{.*\}",
            cleaned,
            re.DOTALL,
        )

        if not match:
            raise ValueError(
                "AI response did not contain valid JSON."
            )

        return json.loads(match.group(0))


def _call_model(
    model: str,
    text: str,
) -> dict:
    """
    Send the complaint to a specific Groq model and
    validate the structured response using Pydantic.
    """

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=1200,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Extract the complaint information "
                    "from the following content:\n\n"
                    f"{text}"
                ),
            },
        ],
    )

    content = response.choices[0].message.content or ""

    raw_data = _extract_json(content)

    validated = AIComplaintExtraction.model_validate(
        raw_data
    )

    return validated.model_dump(mode="json")


def extract_complaint(text: str) -> dict:
    """
    Try the assignment-required model first.

    If Groq rejects/decommissions that model, automatically
    retry using the configured fallback model.
    """

    primary_model = settings.groq_model
    fallback_model = settings.groq_fallback_model

    try:
        return _call_model(
            primary_model,
            text,
        )

    except Exception as primary_error:

        # Do not retry the same model.
        if fallback_model == primary_model:
            raise RuntimeError(
                f"Groq model failed: {primary_error}"
            ) from primary_error

        try:
            result = _call_model(
                fallback_model,
                text,
            )

            return result

        except Exception as fallback_error:
            raise RuntimeError(
                "Both Groq models failed. "
                f"Primary ({primary_model}): "
                f"{primary_error}. "
                f"Fallback ({fallback_model}): "
                f"{fallback_error}."
            ) from fallback_error


# ============================================================
# ROOT CAUSE RECOMMENDATION
# ============================================================

ROOT_CAUSE_SYSTEM_PROMPT = """
You are an AI investigation assistant for a pharmaceutical
customer complaint management system.

Your task is to provide possible root-cause investigation areas
for a customer complaint.

Do NOT claim that any recommendation is a confirmed root cause.

Use only the information provided.

Consider relevant investigation areas such as:
- Raw material variation
- Manufacturing/process parameters
- Environmental or storage conditions
- Packaging/container integrity
- Equipment or process issues
- Laboratory/testing issues
- Documentation or handling issues

Focus on investigation activities rather than diagnosing
a confirmed technical mechanism.

Return ONLY valid JSON using this structure:

{
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2",
    "Recommendation 3"
  ],
  "rationale": "Brief explanation of why these investigation areas are relevant."
}

Provide 3 to 5 focused recommendations.

Do not invent batch results, test results, deviations,
laboratory findings, or confirmed causes.
"""


def _call_root_cause_model(
    model: str,
    complaint_text: str,
) -> dict:
    """
    Generate structured root-cause investigation guidance
    using a specific Groq model.
    """

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=1000,
        messages=[
            {
                "role": "system",
                "content": ROOT_CAUSE_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Identify possible root-cause investigation "
                    "areas for the following complaint:\n\n"
                    f"{complaint_text}"
                ),
            },
        ],
    )

    content = response.choices[0].message.content or ""

    raw_data = _extract_json(content)

    from app.schemas.investigation import RootCauseRecommendation

    validated = RootCauseRecommendation.model_validate(
        raw_data
    )

    return validated.model_dump()


def recommend_root_causes(
    complaint_text: str,
) -> dict:
    """
    Generate root-cause investigation recommendations.

    Uses the configured primary Groq model first and the
    configured fallback model if the primary model fails.
    """

    primary_model = settings.groq_model
    fallback_model = settings.groq_fallback_model

    try:
        return _call_root_cause_model(
            primary_model,
            complaint_text,
        )

    except Exception as primary_error:

        if fallback_model == primary_model:
            raise RuntimeError(
                f"Root cause model failed: {primary_error}"
            ) from primary_error

        try:
            return _call_root_cause_model(
                fallback_model,
                complaint_text,
            )

        except Exception as fallback_error:
            raise RuntimeError(
                "Both Groq models failed for root-cause "
                "recommendation. "
                f"Primary ({primary_model}): "
                f"{primary_error}. "
                f"Fallback ({fallback_model}): "
                f"{fallback_error}."
            ) from fallback_error


# ============================================================
# CAPA RECOMMENDATION
# ============================================================

CAPA_SYSTEM_PROMPT = """
You are an AI quality-system assistant for a pharmaceutical
customer complaint management system.

Your task is to recommend possible Corrective and Preventive Actions
(CAPA) based only on the complaint and investigation information provided.

Corrective actions should address the current complaint or identified
problem.

Preventive actions should reduce the likelihood of recurrence.

Important rules:
- Do not claim that a root cause has been confirmed.
- Do not invent deviations, test results, batch results, laboratory
  findings, or investigation findings.
- Recommendations must be practical and relevant to pharmaceutical
  quality systems.
- Use only the information provided.
- Recommendations are guidance for QA review, not final CAPA decisions.
- Do not automatically assume that a batch failure or manufacturing
  deviation has occurred.
- Recommendations should be framed as actions for QA/investigation
  review.

Return ONLY valid JSON using this structure:

{
  "corrective_actions": [
    "Corrective action 1",
    "Corrective action 2",
    "Corrective action 3"
  ],
  "preventive_actions": [
    "Preventive action 1",
    "Preventive action 2",
    "Preventive action 3"
  ],
  "rationale": "Brief explanation of why these actions are relevant."
}

Provide 2 to 5 focused corrective actions and 2 to 5 focused
preventive actions.
"""


def _call_capa_model(
    model: str,
    complaint_text: str,
) -> dict:
    """
    Generate structured CAPA guidance using a specific Groq model.
    """

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=1200,
        messages=[
            {
                "role": "system",
                "content": CAPA_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Recommend possible corrective and preventive "
                    "actions for the following complaint and "
                    "investigation:\n\n"
                    f"{complaint_text}"
                ),
            },
        ],
    )

    content = response.choices[0].message.content or ""

    raw_data = _extract_json(content)

    from app.schemas.capa import CAPARecommendation

    validated = CAPARecommendation.model_validate(
        raw_data
    )

    return validated.model_dump()


def recommend_capa(
    complaint_text: str,
) -> dict:
    """
    Generate CAPA recommendations.

    Uses the configured primary Groq model first and the
    configured fallback model if the primary model fails.
    """

    primary_model = settings.groq_model
    fallback_model = settings.groq_fallback_model

    try:
        return _call_capa_model(
            primary_model,
            complaint_text,
        )

    except Exception as primary_error:

        if fallback_model == primary_model:
            raise RuntimeError(
                f"CAPA recommendation model failed: "
                f"{primary_error}"
            ) from primary_error

        try:
            return _call_capa_model(
                fallback_model,
                complaint_text,
            )

        except Exception as fallback_error:
            raise RuntimeError(
                "Both Groq models failed for CAPA recommendation. "
                f"Primary ({primary_model}): "
                f"{primary_error}. "
                f"Fallback ({fallback_model}): "
                f"{fallback_error}."
            ) from fallback_error