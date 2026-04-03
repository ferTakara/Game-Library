from fastapi import FastAPI, Request, Response, Depends, Cookie, HTTPException, Form, Query, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import ReviewCreate, ReviewResponse, UserCreate, UserResponse, GameCreate, GameResponse

from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db

from typing import Annotated

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")
templates = Jinja2Templates(directory="templates")

# API calls -------------------------

# Relacionado a usuario
@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    result = db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = result.scalars().first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get(
    "/api/users/{user_id}",
    response_model=UserResponse
)
def find_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if user:
        return user

    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )



# Relacionado a jogo
@app.post(
    "/api/games",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_game(game: GameCreate, db: Annotated[Session, Depends(get_db)]):
    existing_game = db.execute(
        select(models.Game).where(
            models.Game.title == game.title
        )
    ).scalar_one_or_none()
    if existing_game:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game already exists",
        )

    new_game = models.Game(
        title = game.title,
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    return new_game

@app.get(
    "/api/games/{game_id}",
    response_model=GameResponse
)
def find_game(game_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Game).where(models.Game.id == game_id))
    game = result.scalars().first()

    if game:
        return game

    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

@app.delete(
    "/api/games/{game_id}",
    response_model=GameResponse
)
def delete_game(game_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Game).where(models.Game.id == game_id))
    game = result.scalars().first()

    if game:
        db.delete(game)
        db.commit()
        return game

    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )



# Relacionado a reviews
@app.post(
    "/api/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(review: ReviewCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == review.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Game).where(models.Game.id == review.game_id))
    game = result.scalars().first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )


    existing_review = db.execute(
        select(models.Review).where(
            models.Review.user_id == user.id,
            models.Review.game_id == game.id
        )
    ).scalar_one_or_none()
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a review for this game",
        )

    new_review = models.Review(
        user = user,
        user_id = review.user_id,
        game = game,
        game_id = review.game_id,
        score = review.score,
        text = review.text,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review

@app.get(
    "/api/reviews/{review_id}",
    response_model=ReviewResponse
)
def find_review(review_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Review).where(models.Review.id == review_id))
    review = result.scalars().first()

    if review:
        return review

    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

@app.delete(
    "/api/reviews/{review_id}",
    response_model=ReviewResponse
)
def delete_review(review_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Review).where(models.Review.id == review_id))
    review = result.scalars().first()

    if review:
        db.delete(review)
        db.commit()
        return review

    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )



# Home
@app.get("/", include_in_schema=False, name="home")
@app.get("/reviews", include_in_schema=False, name="reviews")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Review))
    reviews = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"reviews": reviews, "title": "Home"},
    )

# Review page
@app.get(
    "/reviews/{review_id}",
    include_in_schema=False, 
    name="reviews_id"
)
def review(review_id : int, request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Review).where(models.Review.id == review_id))
    review = result.scalars().first()

    if review:
        return templates.TemplateResponse(
            request,
            "review.html",
            {"review": review, "title": "Review"},
        )

    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

# User profile
@app.get("/users/{user_id}", include_in_schema=False, name="user_profile")
def user_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Review).where(models.Review.user_id == user_id))
    reviews = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "profile.html",
        {"reviews": reviews, "user": user, "title": f"{user.username}'s Posts"},
    )

# Games Page
@app.get("/games", include_in_schema=False, name="games")
def game_page(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Game))
    games = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "games.html",
        {"games": games, "title": "Home"},
    )

@app.get("/search_games")
def search_games(request: Request, q: str = ""):
    statement = select(Game)

    if q:
        statement = statement.where(Game.title.ilike(f"%{q}%"))

    games = session.exec(statement).all()

    return templates.TemplateResponse(
        "games_results.html",
        {"request": request, "games": games}
    )

# Individual game page 
@app.get(
    "/games/{games_id}",
    include_in_schema=False, 
    name="games_id"
)
def review(games_id : int, request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Game).where(models.Game.id == games_id))
    game = result.scalars().first()

    if game:
        return templates.TemplateResponse(
            request,
            "game_page.html",
            {"game": game, "title": game.title},
        )

    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Game not found"
    )




# Tratamento de erro
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )