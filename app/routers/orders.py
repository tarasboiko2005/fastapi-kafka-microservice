from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import OrderCreate, OrderResponse
from app.repositories.order_repo import OrderRepository
from app.services.order_service import OrderService
from app.dependencies import get_current_user
from app.models import UserDB, OrderStatus

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    repo = OrderRepository(db)
    return OrderService(repo)

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    service: OrderService = Depends(get_order_service),
    current_user: UserDB = Depends(get_current_user)
):
    return await service.create_order(order, current_user.id)

@router.get("/", response_model=list[OrderResponse])
async def read_orders(
    service: OrderService = Depends(get_order_service),
    current_user: UserDB = Depends(get_current_user)
):
    return await service.get_all_orders(current_user.id)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
    current_user: UserDB = Depends(get_current_user)
):
    return await service.get_order_details(order_id, current_user.id)

@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    service: OrderService = Depends(get_order_service),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update the status of a specific order.
    Status must be one of: pending, processing, shipped, delivered, cancelled.
    """
    return await service.update_order_status(order_id, current_user.id, new_status)

@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
    current_user: UserDB = Depends(get_current_user)
):
    return await service.delete_order(order_id, current_user.id)