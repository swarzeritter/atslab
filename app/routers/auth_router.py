import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, PasswordResetToken
from app.auth import verify_password, get_password_hash, create_access_token
from app.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/register")
def register_page(request: Request, current_user=Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url="/posts", status_code=303)
    return templates.TemplateResponse(request, "auth/register.html", {"current_user": None})


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(request, "auth/register.html", {
            "current_user": None,
            "error": "Ім'я користувача вже зайняте",
        })
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(request, "auth/register.html", {
            "current_user": None,
            "error": "Email вже використовується",
        })

    user = User(username=username, email=email, password_hash=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    response = RedirectResponse(url="/posts", status_code=303)
    response.set_cookie("access_token", token, httponly=True, max_age=60 * 60 * 24 * 7)
    return response


@router.get("/login")
def login_page(request: Request, current_user=Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url="/posts", status_code=303)
    return templates.TemplateResponse(request, "auth/login.html", {"current_user": None})


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "auth/login.html", {
            "current_user": None,
            "error": "Невірний email або пароль",
        })

    token = create_access_token(user.id)
    response = RedirectResponse(url="/posts", status_code=303)
    response.set_cookie("access_token", token, httponly=True, max_age=60 * 60 * 24 * 7)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/posts", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/forgot-password")
def forgot_password_page(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse(request, "auth/forgot_password.html", {
        "current_user": current_user,
    })


@router.post("/forgot-password")
def forgot_password(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return templates.TemplateResponse(request, "auth/forgot_password.html", {
            "current_user": current_user,
            "error": "Email не знайдено",
        })

    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used.is_(False),
    ).update({"used": True})

    token_value = secrets.token_urlsafe(32)
    reset_token = PasswordResetToken(
        token=token_value,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(reset_token)
    db.commit()

    reset_link = f"/auth/reset-password/{token_value}"
    return templates.TemplateResponse(request, "auth/forgot_password.html", {
        "current_user": current_user,
        "reset_link": reset_link,
    })


@router.get("/reset-password/{token}")
def reset_password_page(
    request: Request,
    token: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used.is_(False),
        PasswordResetToken.expires_at > datetime.now(timezone.utc),
    ).first()

    if not reset_token:
        return templates.TemplateResponse(request, "auth/reset_password.html", {
            "current_user": current_user,
            "error": "Посилання недійсне або термін дії закінчився",
        })
    return templates.TemplateResponse(request, "auth/reset_password.html", {
        "current_user": current_user, "token": token,
    })


@router.post("/reset-password/{token}")
def reset_password(
    request: Request,
    token: str,
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if password != password_confirm:
        return templates.TemplateResponse(request, "auth/reset_password.html", {
            "current_user": current_user,
            "token": token, "error": "Паролі не співпадають",
        })

    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used.is_(False),
        PasswordResetToken.expires_at > datetime.now(timezone.utc),
    ).first()

    if not reset_token:
        return templates.TemplateResponse(request, "auth/reset_password.html", {
            "current_user": current_user,
            "error": "Посилання недійсне або термін дії закінчився",
        })

    reset_token.user.password_hash = get_password_hash(password)
    reset_token.used = True
    db.commit()

    return RedirectResponse(url="/auth/login?reset=success", status_code=303)
