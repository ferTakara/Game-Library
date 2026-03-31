from fastapi import FastAPI, Request, Response, Depends, Cookie, HTTPException, Form, Query, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import ReviewCreate, ReviewResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

reviews: list[dict] = [
    {
        "id": 1,
        "user": "Sonicao",
        "date_posted": "21/04/2026",
        "score": "10/10",
        "game": "Terraria",
        "text": "Amo terraria"
    },

    {
        "id": 2,
        "user": "EPU",
        "date_posted": "21/04/2026",
        "score": "10/10",
        "game": "Terraria",
        "text": "Amo terraria tbm"
    },
] 

@app.get("/reviews")
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"reviews": reviews, "title": "Home"})

@app.get("/reviews/{review_id}")
def get_review(request: Request, review_id: int):
    for review in reviews:
        if review.get("id") == review_id:
            return templates.TemplateResponse(
                request,
                "review.html",
                {"review": review, "title": "Review"}
            )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

@app.get("/api/reviews", response_model=list[ReviewResponse])
def get_reviews():
    return reviews

@app.post(
    "/api/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(review: ReviewCreate):
    new_id = max(p["id"] for p in reviews) + 1 if reviews else 1
    new_review = {
        "id": new_id,
        "user": review.user,
        "score": review.score,
        "game": review.game,
        "text": review.text,
        "date_posted": "21/04/2026",
    }
    reviews.append(new_review)
    return new_review


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