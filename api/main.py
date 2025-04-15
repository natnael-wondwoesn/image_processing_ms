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


class TaskResponse(BaseModel):
    task_id: str


@app.post("/upload", response_model=TaskResponse)
async def upload_image(file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    file_content = await file.read()

    # Save file temporarily (in production, use a shared volume or cloud storage)
    with open(f"/tmp/{task_id}_{file.filename}", "wb") as f:
        f.write(file_content)

    # Send task to RabbitMQ
    task_data = {"task_id": task_id, "filename": f"{task_id}_{file.filename}"}
    channel.basic_publish(exchange="", routing_key="image_tasks", body=str(task_data))

    return {"task_id": task_id}


@app.get("/status/{task_id}")
async def check_status(task_id: str):
    # In a real system, check task status (e.g., via a database)
    return {"task_id": task_id, "status": "pending"}
