# Blog cá nhân — ducdev (Python)

## Stack
- Python 3.12, Django 6
- Django Admin (viết bài)
- django-ckeditor (rich text editor)
- django-taggit (tags)
- PostgreSQL (production Railway), MySQL (local)
- WhiteNoise (static files)
- Tailwind CSS v4 (standalone CLI, không cần Node.js)
- Railway deploy

## Patterns
- Class-based views (CBV)
- Django ORM, không raw SQL
- Template inheritance với base.html
- Context processor `posts.context_processors.nav_categories` inject `nav_categories` vào mọi template

## Models
Post: title, slug, excerpt, content, thumbnail,
      status (draft/published), published_at,
      reading_time, meta_title, meta_description,
      author (FK User), category (FK Category), tags (TaggableManager)

Category: name, slug, description

Tags: dùng django-taggit

## Packages
pip install django django-ckeditor django-taggit django-extensions
pip install pillow whitenoise psycopg2-binary python-decouple gunicorn
pip install dj-database-url mysqlclient

## Design system
- Background: `#FBFBF8` (warm white)
- Dark: `#15140F`
- Accent: `oklch(0.86 0.2 125)` (lime green)
- Border: `#E8E7E0`
- Muted text: `#8A897E` / `#A8A89C`
- Font heading: Space Grotesk (700)
- Font body: Manrope (400/600)
- Font mono: JetBrains Mono — dùng cho metadata, labels, tags, nav links
- Bo góc: `rounded-sm` (2px) cho buttons/chips, `rounded-sm` (3px) cho ảnh/cards
- Không dùng gradient

## Responsive — áp dụng mọi template
- **Mobile-first**, breakpoints: `sm` 640px · `md` 768px · `lg` 1024px
- Container padding: `px-4 sm:px-6 lg:px-10`
- Grid bài viết: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`
- Hero homepage: `grid-cols-1 lg:grid-cols-2`
- Font size H1 article: `text-3xl sm:text-4xl lg:text-5xl`
- Font size hero title: `text-2xl sm:text-3xl lg:text-5xl`
- Newsletter band: `flex-col md:flex-row`
- Nav: hiện đầy đủ ở `lg+`, hamburger dropdown ở mobile (toggle JS)
- Margin/gap: dùng `gap-6 sm:gap-8`, `py-8 sm:py-12`, `mb-8 sm:mb-12`
- Ảnh thumbnail: luôn `aspect-ratio:16/10`, `object-cover`, `w-full`
- Không dùng width/height cố định px trên mobile

## Tailwind CSS
- Input: `static/css/input.css` — dùng `@import "tailwindcss"` + `@theme {}`
- Output: `static/css/style.css` — minified, commit vào git
- Build: `.\tailwindcss.exe -i .\static\css\input.css -o .\static\css\style.css --minify`
- Watch: `.\tailwindcss.exe -i .\static\css\input.css -o .\static\css\style.css --watch`
- Sau khi sửa template/CSS: **phải build lại** trước khi commit

## Thứ tự build
1. django-admin startproject + startapp posts
2. Models + migrations
3. Django Admin config (Post, Category, Tags)
4. Views + URLs (list, detail, category filter)
5. Templates (base, index, post detail, category)
6. Slug auto + reading time tự tính
7. Static files + Tailwind v4
8. Deploy Railway

## Deploy Railway
### File bắt buộc
- requirements.txt — viết bằng Python, không dùng PowerShell `>` (tránh UTF-16 BOM)
- Procfile: `web: python manage.py collectstatic --noinput && gunicorn blog.wsgi --bind 0.0.0.0:$PORT`
- runtime.txt: `python-3.12.9` (không dùng 3.12.0)
- Không commit `mysqlclient` vào requirements.txt (Railway dùng PostgreSQL)

### Settings
- Dùng python-decouple để đọc biến môi trường
- DEBUG=False trên production
- ALLOWED_HOSTS đọc từ env
- Database: ưu tiên `DATABASE_URL` → fallback `PGHOST` (Railway inject) → fallback MySQL (local)
- WhiteNoise middleware đặt ngay sau SecurityMiddleware
- STATIC_ROOT = BASE_DIR / 'staticfiles'
- STATICFILES_DIRS = [BASE_DIR / 'static']

### Biến môi trường Railway
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=yourdomain.up.railway.app
# DATABASE_URL → Railway tự inject khi add PostgreSQL plugin

### Sau deploy lần đầu (chạy trong Railway shell)
python manage.py migrate
python manage.py createsuperuser
