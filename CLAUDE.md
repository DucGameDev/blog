# Blog cá nhân — ducdev (Python)

## Stack
- Python 3.12, Django 5
- Django Admin (viết bài)
- django-ckeditor (rich text editor)
- django-taggit (tags)
- PostgreSQL
- WhiteNoise (static files)
- Railway deploy

## Patterns
- Class-based views (CBV)
- Django ORM, không raw SQL
- Template inheritance với base.html

## Models
Post: title, slug, excerpt, content, thumbnail,
      status (draft/published), published_at,
      reading_time, meta_title, meta_description,
      author (FK User), category (FK Category)

Category: name, slug, description

Tags: dùng django-taggit

## Packages
pip install django
pip install django-ckeditor
pip install django-taggit
pip install django-extensions
pip install pillow
pip install whitenoise
pip install psycopg2-binary
pip install python-decouple
pip install gunicorn

## Design
- Primary: #7F77DD (purple)
- Font mono cho metadata (ngày, reading time, tags)
- Style: tech/developer blog, clean, monospace feel

## Thứ tự build
1. django-admin startproject + startapp blog
2. Models + migrations
3. Django Admin config (Post, Category, Tags)
4. Views + URLs (list, detail, category filter)
5. Templates (base, index, post detail)
6. Slug auto + reading time tự tính
7. Static files + Tailwind
8. Deploy Railway

## Deploy Railway
### File bắt buộc
- requirements.txt (pip freeze > requirements.txt)
- Procfile: web: python manage.py collectstatic --noinput && gunicorn blog.wsgi --bind 0.0.0.0:$PORT
- runtime.txt: python-3.12.0

### Settings
- Dùng python-decouple để đọc biến môi trường
- DEBUG=False trên production
- ALLOWED_HOSTS đọc từ env
- Database đọc từ PGDATABASE, PGUSER, PGPASSWORD, PGHOST, PGPORT (Railway tự inject)
- WhiteNoise cho static files
- STATIC_ROOT = BASE_DIR / 'staticfiles'

### Biến môi trường cần set trên Railway
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=yourdomain.railway.app
# PGDATABASE, PGUSER, PGPASSWORD, PGHOST, PGPORT → Railway tự inject khi add PostgreSQL plugin

### Sau deploy lần đầu (chạy trong Railway shell)
python manage.py migrate
python manage.py createsuperuser
