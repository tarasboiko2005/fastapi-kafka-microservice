from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str):
        if "gmail.com" not in v:
            raise ValueError('We only accept Gmail!')
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    item_name: str = Field(min_length=3, max_length=50)
    price: int = Field(gt=0, le=1000000, description="Price in cents")


class OrderResponse(BaseModel):
    id: int
    item_name: str
    price: int
    status: str
    owner_id: int

    class Config:
        from_attributes = True