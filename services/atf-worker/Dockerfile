FROM atdd-worker-base

# ATF necesita Playwright para los acceptance tests
RUN pip install --no-cache-dir playwright behave && \
    playwright install --with-deps chromium

CMD [".venv/bin/celery", "-A", "atdd_orchestrator.infrastructure.celery.app", \
     "worker", "--loglevel=info", "--queues=ready-to-atf", "--concurrency=1"]
