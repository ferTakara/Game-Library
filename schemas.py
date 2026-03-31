from pydantic import BaseModel, ConfigDict, Field

class ReviewBase(BaseModel):
    user: str
    score: int
    game: str
    text: str

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: str