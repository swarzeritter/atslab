from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/edit")
def edit_profile_page(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse(request, "profile/edit.html", {
        "current_user": current_user,
    })


@router.post("/edit")
def update_profile(
    request: Request,
    bio: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    current_user.bio = bio
    db.commit()
    return RedirectResponse(url=f"/profile/{current_user.username}", status_code=303)


@router.get("/{username}")
def view_profile(
    request: Request,
    username: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return templates.TemplateResponse(request, "profile/view.html", {
        "profile_user": user, "current_user": current_user,
    })
