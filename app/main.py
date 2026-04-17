from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.database import engine
from app import models
from app.routers import auth_router, posts_router, profile_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog App")
app.add_middleware(SessionMiddleware, secret_key="session-secret-change-in-production")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(posts_router.router, prefix="/posts", tags=["posts"])
app.include_router(profile_router.router, prefix="/profile", tags=["profile"])


@app.get("/")
def root():
    return RedirectResponse(url="/posts")
