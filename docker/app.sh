#!/bin/bash


alembic upgrade head

python seed.py

cd app

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
