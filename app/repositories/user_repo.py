from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import UserDB

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> UserDB | None:
        query = select(UserDB).where(UserDB.username == username)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, username: str, email: str, hashed_password: str) -> UserDB:
        new_user = UserDB(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user