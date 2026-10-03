import os

from dotenv import load_dotenv


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# APPLICATION SETTINGS
# ---------------------------------------------------------

APP_NAME = "RescueMind AI"
APP_VERSION = "2.3"

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
)


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///rescuemind.db"
)


# ---------------------------------------------------------
# AI / GROQ
# ---------------------------------------------------------

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)


# ---------------------------------------------------------
# APPLICATION BEHAVIOUR
# ---------------------------------------------------------

MAX_INCIDENTS_DISPLAY = int(
    os.getenv(
        "MAX_INCIDENTS_DISPLAY",
        "50"
    )
)

MONITORING_INTERVAL_SECONDS = int(
    os.getenv(
        "MONITORING_INTERVAL_SECONDS",
        "10"
    )
)


# ---------------------------------------------------------
# SAFETY SETTINGS
# ---------------------------------------------------------

# AI recommendations must never automatically
# dispatch emergency resources.

HUMAN_APPROVAL_REQUIRED = True

AUTO_DISPATCH_ENABLED = False
AUTO_MERGE_ENABLED = False


# ---------------------------------------------------------
# RESOURCE SETTINGS
# ---------------------------------------------------------

DEFAULT_RESOURCE_SEARCH_RADIUS_KM = float(
    os.getenv(
        "DEFAULT_RESOURCE_SEARCH_RADIUS_KM",
        "50"
    )
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def get_groq_api_key() -> str:
    """
    Return the configured Groq API key.
    """

    return GROQ_API_KEY


def is_groq_configured() -> bool:
    """
    Check whether a Groq API key is available.
    """

    return bool(GROQ_API_KEY)


def get_database_url() -> str:
    """
    Return the configured database URL.
    """

    return DATABASE_URL
