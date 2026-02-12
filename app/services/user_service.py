from fastapi import HTTPException, status
from app.repositories.user_repo import UserRepository
from app.schemas import UserCreate
from app.security import get_password_hash, verify_password, create_access_token

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register_user(self, user_data: UserCreate):
        existing_user = await self.repo.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed_pwd = get_password_hash(user_data.password)

        return await self.repo.create(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_pwd
        )

    async def login_user(self, username: str, password: str):
        user = await self.repo.get_by_username(username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(data={"sub": user.username, "user_id": user.id})

        return {"access_token": access_token, "token_type": "bearer"}