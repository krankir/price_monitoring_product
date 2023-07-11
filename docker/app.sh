#!/bin/bash

alembic upgrade head

cd src

gunicorn main:app --workers 1  --reload --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000