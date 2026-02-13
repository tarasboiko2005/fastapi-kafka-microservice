import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.config import settings
from app.logger import logger

MAX_RETRIES = 3
TOPIC_NAME = "order_events"
DLQ_TOPIC = "orders.failed"


async def send_to_dlq(producer: AIOKafkaProducer, message_value: dict, error: Exception):
    payload = {
        "original_message": message_value,
        "error": str(error),
        "reason": "Max retries reached"
    }
    await producer.send_and_wait(DLQ_TOPIC, json.dumps(payload).encode("utf-8"))
    logger.error(f"💀 [DLQ] Message sent to {DLQ_TOPIC} after {MAX_RETRIES} attempts")


async def process_order_logic(data: dict):

    # if data.get("price") > 1000:
    #     raise Exception("Payment gateway timeout")

    logger.info(f"⚙️ Processing order {data.get('order_id')}...")
    await asyncio.sleep(1)  # Емуляція роботи


async def start_worker():
    consumer = AIOKafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="order_processing_group",
        auto_offset_reset="earliest",
        enable_auto_commit=True
    )
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

    await consumer.start()
    await producer.start()

    logger.info("👷 Worker is UP and listening for 'order_events'...")

    try:
        async for msg in consumer:
            try:
                message_value = json.loads(msg.value.decode("utf-8"))
            except Exception as e:
                logger.error(f"❌ Failed to decode message: {e}")
                continue

            order_id = message_value.get("order_id", "unknown")

            success = False
            for attempt in range(MAX_RETRIES):
                try:
                    await process_order_logic(message_value)
                    success = True
                    logger.info(f"✅ Order {order_id} processed successfully on attempt {attempt + 1}")
                    break
                except Exception as e:
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed for order {order_id}: {e}")
                    if attempt < MAX_RETRIES - 1:
                        wait_time = 2 ** attempt
                        await asyncio.sleep(wait_time)
                    else:
                        await send_to_dlq(producer, message_value, e)

    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(start_worker())