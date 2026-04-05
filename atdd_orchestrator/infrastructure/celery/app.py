from celery import Celery
from atdd_orchestrator.config import REDIS_URL, WORKER_CONCURRENCY

app = Celery(
    "atdd",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["atdd_orchestrator.infrastructure.celery.tasks"],
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    worker_concurrency=WORKER_CONCURRENCY,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "run_test_engineer": {"queue": "inbox"},
        "run_developer":     {"queue": "ready-to-dev"},
        "run_tester":        {"queue": "ready-to-test"},
        "run_atf":           {"queue": "ready-to-atf"},
    },
)
