import pika
import os
from PIL import Image
import ast

rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue="image_tasks")


def process_image(filename: str):
    input_path = f"/tmp/{filename}"
    output_path = f"/tmp/processed_{filename}"

    # Example: Resize image to 50% of original size
    with Image.open(input_path) as img:
        width, height = img.size
        new_size = (width // 2, height // 2)
        img_resized = img.resize(new_size)
        img_resized.save(output_path)

    # Clean up
    os.remove(input_path)


def callback(ch, method, properties, body):
    task_data = ast.literal_eval(body.decode())
    task_id = task_data["task_id"]
    filename = task_data["filename"]

    print(f"Processing task {task_id} for file {filename}")
    process_image(filename)

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(queue="image_tasks", on_message_callback=callback)
print("Worker started. Waiting for tasks...")
channel.start_consuming()
