# Blog App

Simple blog web application built with FastAPI and Jinja2.

## Features

- User registration and login (JWT-based auth via HTTP-only cookies)
- Password reset via token
- Create, edit, and delete posts
- Comments on posts
- User profiles with bio

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Templates | Jinja2 + Bootstrap 5 |
| ORM | SQLAlchemy |
| Database | SQLite |
| Auth | JWT (python-jose) + bcrypt |
| Server | Uvicorn |

## Project Structure

```
Project/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── database.py      # DB engine & session
│   ├── models.py        # SQLAlchemy models
│   ├── auth.py          # JWT & password hashing
│   ├── dependencies.py  # Shared dependencies (get_current_user)
│   └── routers/
│       ├── auth_router.py     # /auth routes
│       ├── posts_router.py    # /posts routes
│       └── profile_router.py  # /profile routes
├── templates/           # Jinja2 HTML templates
│   ├── base.html
│   ├── auth/
│   ├── posts/
│   └── profile/
├── static/
│   └── css/custom.css
├── run.py
└── requirements.txt
```

## Running the App

1. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
python run.py
```

4. Open [http://localhost:8000](http://localhost:8000) in your browser.

The SQLite database (`blog.db`) is created automatically on first run.

## API Docs

FastAPI provides automatic interactive documentation:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
