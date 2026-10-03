import streamlit as st

from utils.database import init_db, get_db
from utils.seed import seed_database
from utils.ui import inject_css, sidebar_navigation
from utils.event_bus import start_worker
from utils.monitoring import process_event

from utils.pages import (
    dashboard_page,
    report_page,
    incidents_page,
    resources_page,
    ai_activity_page,
    live_monitoring_page,
    audit_page,
)


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="RescueMind AI",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# APPLICATION INITIALIZATION
# ---------------------------------------------------------

# Load RescueMind AI professional UI styling
inject_css()

# Initialize database
init_db()

# Insert initial/demo data when required
seed_database()

# Start event-driven monitoring worker
start_worker(process_event)


# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------

page = sidebar_navigation()


# ---------------------------------------------------------
# PAGE ROUTING
# ---------------------------------------------------------

with get_db() as db:

    if page == "Command Center":
        dashboard_page(db)

    elif page == "Report Emergency":
        report_page(db)

    elif page == "Incidents":
        incidents_page(db)

    elif page == "Resources":
        resources_page(db)

    elif page == "AI Activity":
        ai_activity_page(db)

    elif page == "Live Monitoring":
        live_monitoring_page(db)

    elif page == "Audit Trail":
        audit_page(db)
