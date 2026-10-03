from datetime import datetime
from math import sqrt
from typing import Any, Dict, List, Optional

from utils.ai import ask_ai_json


# =========================================================
# INTAKE AGENT
# =========================================================

def intake_agent(
    description: str,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extract structured information from an emergency report.

    The agent identifies signals and missing information.
    It does not treat extracted information as verified fact.
    """

    prompt = f"""
Analyze this emergency report.

Category provided by operator:
{category or "Not provided"}

Description:
{description}

Return valid JSON with exactly these fields:

{{
    "category": "...",
    "signals": [],
    "missing_information": [],
    "urgency_indicators": [],
    "summary": "..."
}}

Rules:
- Use only information contained in the report.
- Do not invent casualties, locations, numbers, or facts.
- If the category is not provided, infer a possible category only
  when the description supports it.
- Missing information should contain useful information that an
  emergency operator may need to verify.
"""

    result = ask_ai_json(
        prompt=prompt,
        system_prompt=(
            "You are the RescueMind AI Intake Agent. "
            "Extract information carefully and distinguish "
            "reported information from assumptions."
        ),
    )

    if not result.get("success", True):
        return {
            "category": category or "unknown",
            "signals": [],
            "missing_information": [
                "AI extraction unavailable"
            ],
            "urgency_indicators": [],
            "summary": description[:500],
        }

    return result


# =========================================================
# LOCATION AGENT
# =========================================================

def location_agent(
    location_text: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Parse and validate incident location information.

    Coordinates are never invented.
    """

    result = {
        "location_text": location_text,
        "latitude": latitude,
        "longitude": longitude,
        "available": False,
        "verified": False,
        "confidence": 0.0,
        "status": "unavailable",
        "reason": "",
    }

    # -----------------------------------------------------
    # Validate coordinates when explicitly supplied
    # -----------------------------------------------------

    if latitude is not None and longitude is not None:

        try:
            lat = float(latitude)
            lon = float(longitude)

            if -90 <= lat <= 90 and -180 <= lon <= 180:

                result.update(
                    {
                        "latitude": lat,
                        "longitude": lon,
                        "available": True,
                        "verified": False,
                        "confidence": 1.0,
                        "status": "coordinates_available",
                        "reason": (
                            "Coordinates were explicitly supplied "
                            "with the emergency report."
                        ),
                    }
                )

                return result

        except (TypeError, ValueError):
            pass

    # -----------------------------------------------------
    # Text-only location
    # -----------------------------------------------------

    if location_text and location_text.strip():

        result.update(
            {
                "available": True,
                "verified": False,
                "confidence": 0.5,
                "status": "text_location_available",
                "reason": (
                    "A textual location was supplied, but "
                    "coordinates are not available."
                ),
            }
        )

        return result

    # -----------------------------------------------------
    # No location
    # -----------------------------------------------------

    result["reason"] = (
        "No reliable location information was supplied."
    )

    return result


# =========================================================
# SEVERITY AGENT
# =========================================================

def severity_agent(
    description: str,
    category: str,
    intake_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Produce a transparent deterministic severity assessment.

    The score is an assessment, not a verified emergency fact.
    """

    text = (
        f"{description} "
        f"{category} "
        f"{str(intake_result or {})}"
    ).lower()

    score = 20
    reasons: List[str] = []

    # -----------------------------------------------------
    # Category-based baseline
    # -----------------------------------------------------

    category_scores = {
        "fire": 35,
        "flood": 35,
        "earthquake": 40,
        "building collapse": 45,
        "medical emergency": 35,
        "road accident": 30,
        "rescue": 35,
        "security": 30,
        "other": 20,
    }

    category_key = category.lower().strip()

    for key, value in category_scores.items():
        if key in category_key:
            score = value
            reasons.append(
                f"Category indicates a baseline severity of {value}."
            )
            break

    # -----------------------------------------------------
    # Signal keywords
    # -----------------------------------------------------

    critical_keywords = {
        "multiple casualties": 25,
        "many injured": 20,
        "trapped": 20,
        "collapse": 20,
        "explosion": 25,
        "large fire": 20,
        "unconscious": 20,
        "critical": 20,
        "life threatening": 20,
    }

    high_keywords = {
        "injured": 10,
        "injury": 10,
        "fire": 10,
        "flood": 10,
        "smoke": 8,
        "danger": 8,
        "trapped": 12,
    }

    for keyword, points in critical_keywords.items():
        if keyword in text:
            score += points
            reasons.append(
                f"Reported signal: '{keyword}'."
            )

    for keyword, points in high_keywords.items():
        if keyword in text:
            score += points
            reasons.append(
                f"Reported signal: '{keyword}'."
            )

    # -----------------------------------------------------
    # Cap score
    # -----------------------------------------------------

    score = min(score, 100)

    if score >= 80:
        level = "critical"
    elif score >= 60:
        level = "high"
    elif score >= 40:
        level = "moderate"
    else:
        level = "low"

    # Example documented assessment:
    # A report with sufficiently strong critical indicators
    # may reach the critical threshold.

    return {
        "score": score,
        "level": level,
        "reasons": reasons,
        "assessment": True,
        "verified_fact": False,
        "timestamp": datetime.utcnow().isoformat(),
    }


# =========================================================
# DUPLICATE DETECTION
# =========================================================

def _tokenize(text: str) -> set:
    """
    Create a simple normalized token set.
    """

    if not text:
        return set()

    cleaned = (
        text.lower()
        .replace(",", " ")
        .replace(".", " ")
        .replace("!", " ")
        .replace("?", " ")
        .replace(":", " ")
        .replace(";", " ")
    )

    return {
        token
        for token in cleaned.split()
        if len(token) > 2
    }


def text_similarity(
    first: str,
    second: str,
) -> float:
    """
    Calculate simple Jaccard text similarity.
    """

    first_tokens = _tokenize(first)
    second_tokens = _tokenize(second)

    if not first_tokens or not second_tokens:
        return 0.0

    intersection = first_tokens.intersection(
        second_tokens
    )

    union = first_tokens.union(
        second_tokens
    )

    if not union:
        return 0.0

    return len(intersection) / len(union)


def coordinate_distance_score(
    lat1: Optional[float],
    lon1: Optional[float],
    lat2: Optional[float],
    lon2: Optional[float],
) -> float:
    """
    Return a simple normalized geographic similarity score.

    This is not a real-world distance calculation.
    It is only used as a lightweight duplicate signal.
    """

    if None in (
        lat1,
        lon1,
        lat2,
        lon2,
    ):
        return 0.0

    try:
        lat_difference = float(lat1) - float(lat2)
        lon_difference = float(lon1) - float(lon2)

        distance = sqrt(
            lat_difference ** 2
            + lon_difference ** 2
        )

        if distance == 0:
            return 1.0

        if distance <= 0.01:
            return 0.9

        if distance <= 0.05:
            return 0.6

        if distance <= 0.1:
            return 0.3

        return 0.0

    except (TypeError, ValueError):
        return 0.0


def duplicate_detection_agent(
    new_report: Dict[str, Any],
    existing_reports: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Compare a new report against existing reports.

    A high similarity is only a recommendation for human review.
    It never automatically merges incidents.
    """

    candidates = []

    new_description = new_report.get(
        "description",
        "",
    )

    new_category = str(
        new_report.get(
            "category",
            "",
        )
    ).lower()

    new_latitude = new_report.get("latitude")
    new_longitude = new_report.get("longitude")

    for report in existing_reports:

        old_description = report.get(
            "description",
            "",
        )

        old_category = str(
            report.get(
                "category",
                "",
            )
        ).lower()

        text_score = text_similarity(
            new_description,
            old_description,
        )

        location_score = coordinate_distance_score(
            new_latitude,
            new_longitude,
            report.get("latitude"),
            report.get("longitude"),
        )

        category_score = (
            1.0
            if new_category
            and old_category
            and new_category == old_category
            else 0.0
        )

        combined_score = (
            text_score * 0.55
            + location_score * 0.30
            + category_score * 0.15
        )

        if combined_score >= 0.45:

            candidates.append(
                {
                    "incident_id": report.get("id"),
                    "incident_code": report.get(
                        "incident_code"
                    ),
                    "similarity_score": round(
                        combined_score,
                        3,
                    ),
                    "text_similarity": round(
                        text_score,
                        3,
                    ),
                    "location_similarity": round(
                        location_score,
                        3,
                    ),
                    "category_match": bool(
                        category_score
                    ),
                }
            )

    candidates.sort(
        key=lambda item: item["similarity_score"],
        reverse=True,
    )

    return {
        "duplicate_candidate": bool(candidates),
        "candidates": candidates[:10],
        "human_review_required": bool(candidates),
        "auto_merge": False,
    }


# =========================================================
# FULL INCIDENT ANALYSIS
# =========================================================

def analyze_incident(
    description: str,
    category: str,
    location_text: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    existing_reports: Optional[
        List[Dict[str, Any]]
    ] = None,
) -> Dict[str, Any]:
    """
    Run the main RescueMind analysis pipeline.
    """

    intake = intake_agent(
        description=description,
        category=category,
    )

    location = location_agent(
        location_text=location_text,
        latitude=latitude,
        longitude=longitude,
    )

    severity = severity_agent(
        description=description,
        category=category,
        intake_result=intake,
    )

    duplicate = duplicate_detection_agent(
        new_report={
            "description": description,
            "category": category,
            "latitude": latitude,
            "longitude": longitude,
        },
        existing_reports=existing_reports or [],
    )

    return {
        "intake": intake,
        "location": location,
        "severity": severity,
        "duplicate": duplicate,
        "analyzed_at": datetime.utcnow().isoformat(),
    }
