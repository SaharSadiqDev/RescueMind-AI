from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import desc

from utils.models import (
    AgentExecution,
    AuditLog,
    Incident,
    IncidentHistory,
    Resource,
    ResourceAssignment,
)


# =========================================================
# INCIDENT SERVICES
# =========================================================

def generate_incident_code(db) -> str:
    """
    Generate the next incident code.
    Example: INC-001, INC-002, ...
    """

    latest = (
        db.query(Incident)
        .order_by(desc(Incident.id))
        .first()
    )

    if latest is None:
        next_number = 1
    else:
        next_number = latest.id + 1

    return f"INC-{next_number:03d}"


def create_incident(
    db,
    category: str,
    description: str,
    location_text: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    severity_score: float = 0,
    severity_level: str = "unknown",
    report_id: Optional[int] = None,
) -> Incident:
    """
    Create and persist a new incident.
    """

    incident_code = generate_incident_code(db)

    incident = Incident(
        incident_code=incident_code,
        report_id=report_id,
        category=category,
        description=description,
        status="open",
        severity_score=severity_score,
        severity_level=severity_level,
        latitude=latitude,
        longitude=longitude,
        location_verified=False,
        duplicate_candidate=False,
        duplicate_confirmed=False,
    )

    db.add(incident)
    db.flush()

    add_incident_history(
        db=db,
        incident_id=incident.id,
        action="Incident created",
        old_status=None,
        new_status="open",
        notes="Incident created through RescueMind AI.",
    )

    return incident


def update_incident_status(
    db,
    incident_id: int,
    new_status: str,
    notes: Optional[str] = None,
) -> Optional[Incident]:
    """
    Update incident status and record the change.
    """

    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        return None

    old_status = incident.status

    incident.status = new_status
    incident.updated_at = datetime.utcnow()

    add_incident_history(
        db=db,
        incident_id=incident.id,
        action="Incident status updated",
        old_status=old_status,
        new_status=new_status,
        notes=notes,
    )

    db.flush()

    return incident


# =========================================================
# INCIDENT HISTORY
# =========================================================

def add_incident_history(
    db,
    incident_id: int,
    action: str,
    old_status: Optional[str] = None,
    new_status: Optional[str] = None,
    notes: Optional[str] = None,
) -> IncidentHistory:
    """
    Add an entry to the incident history.
    """

    history = IncidentHistory(
        incident_id=incident_id,
        action=action,
        old_status=old_status,
        new_status=new_status,
        notes=notes,
    )

    db.add(history)
    db.flush()

    return history


# =========================================================
# AI ACTIVITY
# =========================================================

def record_agent_execution(
    db,
    agent_name: str,
    action: str,
    incident_id: Optional[int] = None,
    status: str = "completed",
    input_data: Optional[str] = None,
    output_data: Optional[str] = None,
) -> AgentExecution:
    """
    Record an AI agent execution for the AI Activity page.
    """

    execution = AgentExecution(
        incident_id=incident_id,
        agent_name=agent_name,
        action=action,
        status=status,
        input_data=input_data,
        output_data=output_data,
    )

    db.add(execution)
    db.flush()

    return execution


# =========================================================
# AUDIT TRAIL
# =========================================================

def record_audit(
    db,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[str] = None,
    user_id: Optional[int] = None,
) -> AuditLog:
    """
    Record an operational audit entry.
    """

    audit = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )

    db.add(audit)
    db.flush()

    return audit


# =========================================================
# RESOURCE SERVICES
# =========================================================

def get_available_resources(
    db,
    resource_type: Optional[str] = None,
) -> List[Resource]:
    """
    Return currently available resources.
    """

    query = (
        db.query(Resource)
        .filter(
            Resource.status == "available"
        )
    )

    if resource_type:
        query = query.filter(
            Resource.resource_type == resource_type
        )

    return query.order_by(
        Resource.id
    ).all()


def update_resource_status(
    db,
    resource_id: int,
    new_status: str,
) -> Optional[Resource]:
    """
    Update resource status.

    Dispatch decisions remain subject to human approval.
    """

    resource = (
        db.query(Resource)
        .filter(Resource.id == resource_id)
        .first()
    )

    if resource is None:
        return None

    resource.status = new_status

    db.flush()

    return resource


# =========================================================
# RESOURCE RECOMMENDATIONS
# =========================================================

def create_resource_recommendation(
    db,
    incident_id: int,
    resource_id: int,
    score: float,
) -> ResourceAssignment:
    """
    Create a resource recommendation.

    The recommendation does NOT dispatch the resource.
    """

    assignment = ResourceAssignment(
        incident_id=incident_id,
        resource_id=resource_id,
        status="recommended",
        recommendation_score=score,
    )

    db.add(assignment)
    db.flush()

    return assignment


def approve_resource_assignment(
    db,
    assignment_id: int,
    approved_by: str,
) -> Optional[ResourceAssignment]:
    """
    Approve a resource recommendation.

    This is an explicit human approval action.
    """

    assignment = (
        db.query(ResourceAssignment)
        .filter(
            ResourceAssignment.id == assignment_id
        )
        .first()
    )

    if assignment is None:
        return None

    assignment.status = "approved"
    assignment.approved_by = approved_by

    db.flush()

    return assignment


def reject_resource_assignment(
    db,
    assignment_id: int,
    reason: Optional[str] = None,
) -> Optional[ResourceAssignment]:
    """
    Reject a resource recommendation.
    """

    assignment = (
        db.query(ResourceAssignment)
        .filter(
            ResourceAssignment.id == assignment_id
        )
        .first()
    )

    if assignment is None:
        return None

    assignment.status = "rejected"

    db.flush()

    return assignment


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

def get_incident_statistics(
    db,
) -> Dict[str, Any]:
    """
    Return summary statistics for the Command Center.
    """

    incidents = (
        db.query(Incident)
        .order_by(desc(Incident.created_at))
        .all()
    )

    total = len(incidents)

    active = sum(
        1
        for incident in incidents
        if incident.status
        not in {"resolved", "closed"}
    )

    critical = sum(
        1
        for incident in incidents
        if incident.severity_level == "critical"
    )

    high = sum(
        1
        for incident in incidents
        if incident.severity_level == "high"
    )

    return {
        "total": total,
        "active": active,
        "critical": critical,
        "high": high,
    }
