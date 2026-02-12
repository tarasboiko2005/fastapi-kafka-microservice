import asyncio
import json
from aiokafka import AIOKafkaConsumer
from app.config import settings


async def run_service_consumer(service_name: str, group_id: str):
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id,
        auto_offset_reset="earliest"
    )
    await consumer.start()
    print(f"✅ [{service_name}] Service started. Listening as group: '{group_id}'")

    try:
        async for msg in consumer:
            payload = json.loads(msg.value.decode('utf-8'))
            order_id = payload.get("order_id")
            price = payload.get("price")

            if service_name == "WAREHOUSE":
                print(f"📦 [Warehouse] Reserving stock for order #{order_id}...")
                await asyncio.sleep(0.5)

            elif service_name == "EMAIL":
                print(f"📧 [Email] Sending receipt for {price} USD for order #{order_id}...")

            elif service_name == "ANALYTICS":
                print(f"📊 [Analytics] +{price} added to report. The boss will be happy!")

    except Exception as e:
        print(f"❌ [{service_name}] Error: {e}")
    finally:
        await consumer.stop()


async def main():

    await asyncio.gather(
        run_service_consumer(service_name="WAREHOUSE", group_id="inventory_group"),
        run_service_consumer(service_name="EMAIL", group_id="notification_group"),
        run_service_consumer(service_name="ANALYTICS", group_id="data_team_group"),
    )


if __name__ == "__main__":
    asyncio.run(main())