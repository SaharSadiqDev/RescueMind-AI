from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from utils.database import Base


# =========================================================
# USER
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    role = Column(String(50), default="operator")

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================================
# EMERGENCY REPORT
# =========================================================

class EmergencyReport(Base):
    __tablename__ = "emergency_reports"

    id = Column(Integer, primary_key=True, index=True)

    incident_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    category = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    location_text = Column(
        String(500),
        nullable=True
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    evidence_path = Column(
        String(500),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    incident = relationship(
        "Incident",
        back_populates="report",
        uselist=False
    )


# =========================================================
# INCIDENT
# =========================================================

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    incident_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    report_id = Column(
        Integer,
        ForeignKey("emergency_reports.id"),
        nullable=True
    )

    category = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        default="open"
    )

    severity_score = Column(
        Float,
        default=0
    )

    severity_level = Column(
        String(50),
        default="unknown"
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    location_verified = Column(
        Boolean,
        default=False
    )

    duplicate_candidate = Column(
        Boolean,
        default=False
    )

    duplicate_confirmed = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    report = relationship(
        "EmergencyReport",
        back_populates="incident"
    )

    location = relationship(
        "IncidentLocation",
        back_populates="incident",
        uselist=False
    )

    evidence = relationship(
        "IncidentEvidence",
        back_populates="incident"
    )

    history = relationship(
        "IncidentHistory",
        back_populates="incident"
    )

    assignments = relationship(
        "ResourceAssignment",
        back_populates="incident"
    )


# =========================================================
# INCIDENT LOCATION
# =========================================================

class IncidentLocation(Base):
    __tablename__ = "incident_locations"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=False
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    location_text = Column(
        String(500),
        nullable=True
    )

    confidence = Column(
        Float,
        default=0
    )

    verified = Column(
        Boolean,
        default=False
    )

    incident = relationship(
        "Incident",
        back_populates="location"
    )


# =========================================================
# INCIDENT EVIDENCE
# =========================================================

class IncidentEvidence(Base):
    __tablename__ = "incident_evidence"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=False
    )

    evidence_type = Column(
        String(50),
        nullable=False
    )

    content = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    incident = relationship(
        "Incident",
        back_populates="evidence"
    )


# =========================================================
# RESOURCE
# =========================================================

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(150),
        nullable=False
    )

    resource_type = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(50),
        default="available"
    )

    capacity = Column(
        Integer,
        default=1
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    capability = Column(
        String(500),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    assignments = relationship(
        "ResourceAssignment",
        back_populates="resource"
    )


# =========================================================
# RESOURCE ASSIGNMENT
# =========================================================

class ResourceAssignment(Base):
    __tablename__ = "resource_assignments"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=False
    )

    resource_id = Column(
        Integer,
        ForeignKey("resources.id"),
        nullable=False
    )

    status = Column(
        String(50),
        default="recommended"
    )

    recommendation_score = Column(
        Float,
        default=0
    )

    approved_by = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    incident = relationship(
        "Incident",
        back_populates="assignments"
    )

    resource = relationship(
        "Resource",
        back_populates="assignments"
    )


# =========================================================
# AGENT EXECUTION
# =========================================================

class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=True
    )

    agent_name = Column(
        String(100),
        nullable=False
    )

    action = Column(
        String(255),
        nullable=False
    )

    status = Column(
        String(50),
        default="completed"
    )

    input_data = Column(
        Text,
        nullable=True
    )

    output_data = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================================
# INCIDENT HISTORY
# =========================================================

class IncidentHistory(Base):
    __tablename__ = "incident_history"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=False
    )

    action = Column(
        String(255),
        nullable=False
    )

    old_status = Column(
        String(50),
        nullable=True
    )

    new_status = Column(
        String(50),
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    incident = relationship(
        "Incident",
        back_populates="history"
    )


# =========================================================
# AUDIT LOG
# =========================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    action = Column(
        String(255),
        nullable=False
    )

    entity_type = Column(
        String(100),
        nullable=True
    )

    entity_id = Column(
        Integer,
        nullable=True
    )

    details = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================================
# RESOURCE OPTIMIZATION RUN
# =========================================================

class ResourceOptimizationRun(Base):
    __tablename__ = "resource_optimization_runs"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=True
    )

    recommendation = Column(
        Text,
        nullable=True
    )

    reasoning = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================================
# EVENT RECORD
# =========================================================

class EventRecord(Base):
    __tablename__ = "event_records"

    id = Column(Integer, primary_key=True, index=True)

    event_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    incident_id = Column(
        Integer,
        nullable=True
    )

    resource_id = Column(
        Integer,
        nullable=True
    )

    payload = Column(
        Text,
        nullable=True
    )

    processed = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
