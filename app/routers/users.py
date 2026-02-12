from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm # <-- Стандартна форма логіна
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import UserCreate, UserResponse
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repo = UserRepository(db)
    return UserService(repo)

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)):
    return await service.register_user(user_data)

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service)):
    return await service.login_user(form_data.username, form_data.password)