from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import OrderDB, OrderStatus

class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, item_name: str, price: int, owner_id: int) -> OrderDB:
        new_order = OrderDB(
            item_name=item_name,
            price=price,
            owner_id=owner_id
        )
        self.db.add(new_order)
        await self.db.commit()
        await self.db.refresh(new_order)
        return new_order

    async def get_by_id(self, order_id: int) -> OrderDB | None:
        query = select(OrderDB).where(OrderDB.id == order_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update_status(self, order_id: int, new_status: OrderStatus) -> OrderDB:
        query = select(OrderDB).where(OrderDB.id == order_id)
        result = await self.db.execute(query)
        order = result.scalars().first()

        if order:
            order.status = new_status
            await self.db.commit()
            await self.db.refresh(order)

        return order

    async def delete(self, order_id: int) -> bool:
        order = await self.get_by_id(order_id)
        if order:
            await self.db.delete(order)
            await self.db.commit()
            return True
        return False

    async def get_all(self, user_id: int) -> list[OrderDB]:
        query = select(OrderDB).where(OrderDB.owner_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()