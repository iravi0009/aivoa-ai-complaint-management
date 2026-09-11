import json
import re

from groq import Groq

from app.core.config import settings


client = Groq(
    api_key=settings.groq_api_key,
)


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
    Send the complaint to a specific Groq model.
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

    return _extract_json(content)


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