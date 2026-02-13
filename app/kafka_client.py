from aiokafka import AIOKafkaProducer
import json
from app.config import settings
from app.logger import logger

producer = None

async def start_kafka_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    logger.info("✅ Kafka Producer Started")

async def stop_kafka_producer():
    if producer:
        await producer.stop()
        logger.info("🛑 Kafka Producer Stopped")

async def send_order_event(order_data: dict):
    if producer is None:
        logger.error("❌ Kafka producer is not initialized")
        raise RuntimeError("Kafka producer is not initialized")

    try:
        user_id = order_data.get("user_id")
        key = str(user_id).encode('utf-8') if user_id else None

        value_json = json.dumps(order_data).encode('utf-8')

        await producer.send_and_wait(
            settings.KAFKA_TOPIC,
            value=value_json,
            key=key
        )
        logger.info(f"📤 Event sent to Kafka topic '{settings.KAFKA_TOPIC}' for order {order_data.get('order_id')}")

    except Exception as e:
        logger.error(f"❌ Error sending to Kafka: {e}")