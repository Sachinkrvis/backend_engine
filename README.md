for running the code:
steps:
    1: uvicorn app.main:app --reload

    2: celery -A app.tasks worker --pool=solo --loglevel=info 