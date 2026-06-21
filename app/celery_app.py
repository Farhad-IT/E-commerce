import os
from datetime import timedelta

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")

celery_app = Celery(
    "celery_app",
    broker=f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//",
    backend="rpc://",
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    result_expires=timedelta(hours=1),
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)
celery_app.conf.task_acks_late = False
celery_app.autodiscover_tasks(["app.worker"])
