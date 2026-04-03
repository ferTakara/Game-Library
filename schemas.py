from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr
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

    
class GameBase(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    bio: Optional[str] = Field(
        default="One of the games of all time",
        max_length=400
    )

class GameCreate(GameBase):
    pass

class GameResponse(GameBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None
    image_path: str | None



class ReviewBase(BaseModel):
    score: int
    text: str

class ReviewCreate(ReviewBase):
    user_id: int #TEMPORARIO
    game_id: int


class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    game_id: int
    date_posted: datetime
    user: UserResponse
    game: GameResponse