"""
Populate the blog database with test data before stress testing.
Run from the Project directory: python tests/load/populate_db.py

Creates:
  - 20 test users
  - 500 posts
  - 2000 comments

This ensures query performance stays stable during the stress test
(the 1st and 1000th insert should behave similarly).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash

models.Base.metadata.create_all(bind=engine)

USERS = 20
POSTS_PER_USER = 25   # 20 * 25 = 500 posts
COMMENTS_PER_POST = 4  # 500 * 4 = 2000 comments

db = SessionLocal()

print("Creating users...")
users = []
for i in range(1, USERS + 1):
    existing = db.query(models.User).filter(models.User.email == f"stress{i}@test.com").first()
    if not existing:
        user = models.User(
            username=f"stressuser{i}",
            email=f"stress{i}@test.com",
            password_hash=get_password_hash("stresspass123"),
        )
        db.add(user)
        users.append(user)
    else:
        users.append(existing)

db.commit()
for u in users:
    db.refresh(u)

print(f"  {len(users)} users ready")

print("Creating posts...")
post_count = 0
all_posts = []
for user in users:
    existing_count = db.query(models.Post).filter(models.Post.author_id == user.id).count()
    to_create = POSTS_PER_USER - existing_count
    for j in range(to_create):
        post = models.Post(
            title=f"Stress post {user.username} #{j}",
            content="This post was created for stress testing. " * 10,
            author_id=user.id,
        )
        db.add(post)
        post_count += 1
    if post_count % 100 == 0 and post_count > 0:
        db.commit()

db.commit()
all_posts = db.query(models.Post).all()
print(f"  {len(all_posts)} posts ready")

print("Creating comments...")
comment_count = 0
for post in all_posts[:100]:  # comment on first 100 posts
    existing_count = db.query(models.Comment).filter(models.Comment.post_id == post.id).count()
    to_create = COMMENTS_PER_POST - existing_count
    for k in range(to_create):
        author = users[k % len(users)]
        comment = models.Comment(
            content=f"Stress test comment #{k}. " * 3,
            post_id=post.id,
            author_id=author.id,
        )
        db.add(comment)
        comment_count += 1
    if comment_count % 200 == 0 and comment_count > 0:
        db.commit()

db.commit()
db.close()

total_comments = comment_count
print(f"  {total_comments} comments ready")
print("\nDatabase populated. Ready for stress testing.")
print("k6 test user: stress1@test.com / stresspass123")
