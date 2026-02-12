from aiokafka import AIOKafkaProducer
import json
from app.config import settings

producer = None

async def start_kafka_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    print("✅ Kafka Producer Started")


async def stop_kafka_producer():
    global producer
    if producer:
        await producer.stop()
        print("🛑 Kafka Producer Stopped")


async def send_order_event(order_data: dict):
    if not producer:
        raise RuntimeError("Kafka producer is not initialized")

    try:
        value_json = json.dumps(order_data).encode('utf-8')
        await producer.send_and_wait(settings.kafka_topic, value_json)
    except Exception as e:
        print(f"❌ Error sending to Kafka: {e}")