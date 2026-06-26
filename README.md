# ducdev blog

Blog cá nhân viết bằng Django, deploy trên Railway.

## Stack

| Thành phần | Chi tiết |
|---|---|
| Backend | Python 3.12, Django 6 |
| Database | PostgreSQL (production), MySQL (local) |
| Rich text | django-ckeditor |
| Tags | django-taggit |
| Static files | WhiteNoise |
| CSS | Tailwind CSS v4 (standalone CLI) |
| Deploy | Railway |

## Cài đặt local

```bash
# Clone và tạo virtual environment
git clone <repo-url>
cd blog
python -m venv venv
venv\Scripts\activate  # Windows

# Cài packages
pip install -r requirements.txt
pip install mysqlclient  # local MySQL

# Tạo file .env
cp .env.example .env  # chỉnh sửa các biến

# Migrate và chạy
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Biến môi trường (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Local MySQL
DB_NAME=blogdb
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# Production — Railway tự inject DATABASE_URL
```

## Tailwind CSS

```bash
# Build một lần
.\tailwindcss.exe -i .\static\css\input.css -o .\static\css\style.css --minify

# Watch mode (development)
.\tailwindcss.exe -i .\static\css\input.css -o .\static\css\style.css --watch
```

Sau khi sửa template hoặc CSS, phải build lại trước khi commit.

## Management commands

```bash
# Tạo bài draft từ JSON (dùng với Claude Code)
python manage.py create_post --json '{"title": "...", "content": "..."}'

# Export toàn bộ bài viết
python manage.py export_posts

# Import bài viết từ file JSON
python manage.py import_posts --file posts_export.json
```

## Cấu trúc project

```
blog/          — Django project settings, URLs
posts/         — App chính
  models.py    — Post, Category, Subscriber, Comment
  views.py     — CBV: list, detail, category, tag, search
  feeds.py     — RSS feed
  sitemaps.py  — XML sitemap
  management/commands/
    create_post.py
    export_posts.py
    import_posts.py
static/css/
  input.css    — Tailwind source
  style.css    — Output (minified, commit vào git)
templates/
  base.html
  posts/index.html, detail.html, category.html, tag.html, search.html
  about.html
```

## Deploy Railway

1. Push code lên GitHub
2. Tạo project Railway, connect repo
3. Add PostgreSQL plugin — Railway tự inject `DATABASE_URL`
4. Set biến môi trường: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`
5. Deploy tự động khi push

```bash
# Sau deploy lần đầu (Railway shell)
python manage.py migrate
python manage.py createsuperuser
```

## URLs chính

| URL | Mô tả |
|---|---|
| `/` | Trang chủ — danh sách bài |
| `/bai-viet/<slug>/` | Chi tiết bài viết |
| `/chu-de/<slug>/` | Lọc theo category |
| `/tag/<slug>/` | Lọc theo tag |
| `/tim-kiem/` | Tìm kiếm |
| `/gioi-thieu/` | Trang about |
| `/feed/` | RSS feed |
| `/sitemap.xml` | Sitemap |
| `/admin/` | Django Admin |
