from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Post, Comment
from app.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("")
def list_posts(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    return templates.TemplateResponse("posts/list.html", {
        "request": request, "posts": posts, "current_user": current_user,
    })


@router.get("/new")
def new_post_page(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("posts/form.html", {
        "request": request, "current_user": current_user, "post": None,
    })


@router.post("")
def create_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)

    post = Post(title=title, content=content, author_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return RedirectResponse(url=f"/posts/{post.id}", status_code=303)


@router.get("/{post_id}")
def post_detail(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не знайдено")
    return templates.TemplateResponse("posts/detail.html", {
        "request": request, "post": post, "current_user": current_user,
    })


@router.get("/{post_id}/edit")
def edit_post_page(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не знайдено")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає доступу")
    return templates.TemplateResponse("posts/form.html", {
        "request": request, "post": post, "current_user": current_user,
    })


@router.post("/{post_id}/edit")
def update_post(
    request: Request,
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не знайдено")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає доступу")

    post.title = title
    post.content = content
    db.commit()
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)


@router.post("/{post_id}/delete")
def delete_post(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не знайдено")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає доступу")

    db.delete(post)
    db.commit()
    return RedirectResponse(url="/posts", status_code=303)


@router.post("/{post_id}/comments")
def add_comment(
    request: Request,
    post_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не знайдено")

    comment = Comment(content=content, post_id=post_id, author_id=current_user.id)
    db.add(comment)
    db.commit()
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)


@router.post("/{post_id}/comments/{comment_id}/delete")
def delete_comment(
    request: Request,
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    comment = db.query(Comment).filter(
        Comment.id == comment_id, Comment.post_id == post_id
    ).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Коментар не знайдено")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає доступу")

    db.delete(comment)
    db.commit()
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)
