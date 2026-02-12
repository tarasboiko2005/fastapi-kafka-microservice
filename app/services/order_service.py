from fastapi import HTTPException, status
from app.schemas import OrderCreate
from app.kafka_client import send_order_event
from app.repositories.order_repo import OrderRepository


class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    async def create_order(self, order_data: OrderCreate, user_id: int):
        new_order = await self.repo.create(
            item_name=order_data.item_name,
            price=order_data.price,
            owner_id=user_id
        )

        event_data = {
            "event": "OrderCreated",
            "order_id": new_order.id,
            "user_id": new_order.owner_id,
            "item": new_order.item_name,
            "price": new_order.price,
            "status": new_order.status
        }
        await send_order_event(event_data)

        return new_order

    async def get_all_orders(self, user_id: int):
        return await self.repo.get_all(user_id)


    async def get_order_details(self, order_id: int, user_id: int):
        order = await self.repo.get_by_id(order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        if order.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this order"
            )

        return order

    async def delete_order(self, order_id: int, user_id: int):
        order = await self.repo.get_by_id(order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        if order.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this order"
            )

        await self.repo.delete(order_id)

        event_data = {
            "event": "OrderCancelled",
            "order_id": order_id,
            "user_id": user_id
        }

        await send_order_event(event_data)
        return {"message": "Order deleted successfully"}