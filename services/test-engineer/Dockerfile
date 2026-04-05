FROM atdd-worker-base

CMD [".venv/bin/celery", "-A", "atdd_orchestrator.infrastructure.celery.app", \
     "worker", "--loglevel=info", "--queues=inbox", "--concurrency=1"]
