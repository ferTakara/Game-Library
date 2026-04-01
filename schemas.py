from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_lenght=50)
    email: EmailStr = Field(max_lenght=120)
    bio: Optional[str] = Field(
        default="Hi! I'm new here!",
        max_length=400
    )

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None
    image_path: str | None


class ReviewBase(BaseModel):
    score: int
    game: str
    text: str

class ReviewCreate(ReviewBase):
    user_id: int #TEMPORARIO


class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    user: UserResponse