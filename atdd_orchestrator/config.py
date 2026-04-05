import os

REDIS_URL          = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
POLL_INTERVAL      = int(os.environ.get("POLL_INTERVAL", "30"))
WORKER_CONCURRENCY = int(os.environ.get("WORKER_CONCURRENCY", "1"))
OPENCODE_BIN       = os.environ.get("OPENCODE_BIN", "opencode")

TIMEOUTS: dict[str, int] = {
    "test_engineer": int(os.environ.get("TIMEOUT_TEST_ENGINEER", "1800")),
    "developer":     int(os.environ.get("TIMEOUT_DEVELOPER",     "3600")),
    "tester":        int(os.environ.get("TIMEOUT_TESTER",        "1800")),
    "atf":           int(os.environ.get("TIMEOUT_ATF",           "1800")),
}

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

PROJECTS_FILE = os.environ.get("PROJECTS_FILE", "projects.yml")
GIT_USER_NAME  = os.environ.get("GIT_USER_NAME", "atdd-orchestrator")
GIT_USER_EMAIL = os.environ.get("GIT_USER_EMAIL", "atdd@orchestrator.local")
