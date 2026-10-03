import json
from typing import Any, Dict, Optional

from groq import Groq

from utils.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
)


# =========================================================
# GROQ CLIENT
# =========================================================

_client: Optional[Groq] = None


def get_groq_client() -> Optional[Groq]:
    """
    Create and return the Groq client when an API key
    is configured.
    """

    global _client

    if not GROQ_API_KEY:
        return None

    if _client is None:
        _client = Groq(
            api_key=GROQ_API_KEY
        )

    return _client


# =========================================================
# BASIC AI REQUEST
# =========================================================

def ask_ai(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.2,
) -> str:
    """
    Send a request to the configured Groq model.

    If the API is unavailable, return a safe message
    instead of crashing the application.
    """

    client = get_groq_client()

    if client is None:
        return (
            "AI service is not configured. "
            "Please add GROQ_API_KEY to the application secrets."
        )

    try:
        messages = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=temperature,
        )

        return response.choices[0].message.content or ""

    except Exception as exc:
        return f"AI request failed: {exc}"


# =========================================================
# STRUCTURED AI RESPONSE
# =========================================================

def ask_ai_json(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.1,
) -> Dict[str, Any]:
    """
    Ask the AI for JSON output and safely parse it.
    """

    json_instruction = """
Return the response as valid JSON only.
Do not include markdown fences.
Do not include additional explanation outside the JSON.
"""

    full_system_prompt = (
        f"{system_prompt}\n\n{json_instruction}"
    )

    response = ask_ai(
        prompt=prompt,
        system_prompt=full_system_prompt,
        temperature=temperature,
    )

    try:
        return json.loads(response)

    except json.JSONDecodeError:
        # Try to recover JSON if the model accidentally
        # returned surrounding text.
        start = response.find("{")
        end = response.rfind("}")

        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(
                    response[start:end + 1]
                )
            except json.JSONDecodeError:
                pass

    return {
        "success": False,
        "raw_response": response,
    }


# =========================================================
# EMERGENCY EXPLANATION
# =========================================================

def generate_incident_explanation(
    category: str,
    description: str,
    severity_level: str,
    severity_score: float,
    location: str = "Unknown",
) -> str:
    """
    Generate a concise natural-language explanation
    for an incident assessment.

    AI output is explanatory only. It does not represent
    a verified emergency fact.
    """

    prompt = f"""
Analyze the following emergency incident.

Category:
{category}

Description:
{description}

Severity assessment:
{severity_level}

Severity score:
{severity_score}/100

Location:
{location}

Provide a concise emergency-operations explanation covering:

1. What was reported.
2. Why the current severity assessment was reached.
3. Important operational concerns.
4. What information may still need verification.

Do not invent facts, coordinates, casualties, resources,
or information that was not provided.
Clearly distinguish reported information from assessment.
"""

    return ask_ai(
        prompt=prompt,
        system_prompt=(
            "You are an emergency intelligence assistant. "
            "Be factual, concise, transparent, and safety-aware. "
            "Never invent missing information."
        ),
        temperature=0.2,
    )


# =========================================================
# INCIDENT SUMMARY
# =========================================================

def generate_incident_summary(
    incident: Dict[str, Any],
) -> str:
    """
    Generate an operator-friendly incident summary.
    """

    prompt = f"""
Create a short emergency operations summary from this
incident data:

{json.dumps(incident, default=str, indent=2)}

Use only the supplied information.
Do not invent missing facts.
Mention uncertainty where appropriate.
"""

    return ask_ai(
        prompt=prompt,
        system_prompt=(
            "You are an emergency operations center "
            "intelligence assistant."
        ),
        temperature=0.2,
    )


# =========================================================
# RESOURCE RECOMMENDATION EXPLANATION
# =========================================================

def explain_resource_recommendation(
    incident: Dict[str, Any],
    resources: list,
) -> str:
    """
    Explain why the listed resources may be relevant.

    This function only explains recommendations.
    It never dispatches resources.
    """

    prompt = f"""
Review this incident:

{json.dumps(incident, default=str, indent=2)}

Candidate resources:

{json.dumps(resources, default=str, indent=2)}

Explain:

- Which resource types appear relevant.
- What capabilities matter.
- Any availability or location concerns.
- Any important uncertainty.

Do not dispatch or assign any resource.
Do not invent resource availability.
"""

    return ask_ai(
        prompt=prompt,
        system_prompt=(
            "You are a resource-planning assistant for an "
            "emergency operations center. Human approval is "
            "always required before dispatch."
        ),
        temperature=0.2,
    )
