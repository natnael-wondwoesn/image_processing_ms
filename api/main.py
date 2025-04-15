from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import pika
import uuid
import os

app = FastAPI()

# RabbitMQ connection
rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue="image_tasks")
