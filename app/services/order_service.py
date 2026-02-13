from fastapi import HTTPException, status
from app.schemas import OrderCreate
from app.kafka_client import send_order_event
from app.repositories.order_repo import OrderRepository
from app.logger import logger
from app.models import OrderStatus  # Імпортуємо наш Enum


class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    async def create_order(self, order_data: OrderCreate, user_id: int):
        logger.info(f"📦 Starting order creation for user {user_id}: {order_data.item_name}")
        new_order = await self.repo.create(
            item_name=order_data.item_name,
            price=order_data.price,
            owner_id=user_id
        )
        logger.info(f"✅ Order {new_order.id} saved to DB with status: {new_order.status}")
        event_data = {
            "event": "OrderCreated",
            "order_id": new_order.id,
            "user_id": new_order.owner_id,
            "item": new_order.item_name,
            "price": new_order.price,
            "status": new_order.status
        }

        await send_order_event(event_data)
        logger.info(f"📤 Kafka: OrderCreated event sent for order {new_order.id}")

        return new_order

    async def get_all_orders(self, user_id: int):
        logger.info(f"🔍 Fetching all orders for user {user_id}")
        return await self.repo.get_all(user_id)

    async def get_order_details(self, order_id: int, user_id: int):
        order = await self.repo.get_by_id(order_id)

        if not order:
            logger.warning(f"❓ Order {order_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        if order.owner_id != user_id:
            logger.warning(f"🚫 User {user_id} tried to access order {order_id} owned by {order.owner_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this order"
            )

        return order

    async def update_order_status(self, order_id: int, user_id: int, new_status: OrderStatus):
        order = await self.get_order_details(order_id, user_id)
        logger.info(f"🔄 Updating order {order_id} status: {order.status} -> {new_status}")
        updated_order = await self.repo.update_status(order_id, new_status)
        event_data = {
            "event": "OrderStatusUpdated",
            "order_id": order_id,
            "new_status": updated_order.status,
            "user_id": user_id
        }
        await send_order_event(event_data)
        logger.info(f"📤 Kafka: OrderStatusUpdated event sent for order {order_id}")

        return updated_order

    async def delete_order(self, order_id: int, user_id: int):
        await self.get_order_details(order_id, user_id)

        await self.repo.delete(order_id)
        logger.info(f"🗑️ Order {order_id} deleted from DB by user {user_id}")
        event_data = {
            "event": "OrderCancelled",
            "order_id": order_id,
            "user_id": user_id
        }

        await send_order_event(event_data)
        logger.info(f"📤 Kafka: OrderCancelled event sent for order {order_id}")

        return {"message": "Order deleted successfully"}