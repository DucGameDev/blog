# Blog cá nhân — ducdev (Python)

## Stack
- Python 3.12, Django 6
- Django Admin (viết bài)
- django-ckeditor (rich text editor)
- django-taggit (tags)
- django-import-export (import/export bài viết)
- PostgreSQL (production Railway), MySQL (local dev)
- WhiteNoise (static files)
- Tailwind CSS v4 (standalone CLI, không cần Node.js)
- Railway deploy

## Patterns
- Class-based views (CBV)
- Django ORM, không raw SQL
- Template inheritance với base.html
- Context processor `posts.context_processors.nav_categories` inject `nav_categories` vào mọi template

## Models
Post: title, slug, excerpt, content, thumbnail (URLField),
      status (draft/published), published_at,
      reading_time, views, meta_title, meta_description,
      author (FK User), category (FK Category), tags (TaggableManager)

Category: name, slug, description
Subscriber: email, subscribed_at, active
Comment: post (FK), name, email, content, created_at, approved

## Templates
- `base.html` — layout chính, nav + footer
- `posts/index.html` — trang chủ, hero + danh sách bài
- `posts/detail.html` — chi tiết bài viết
- `posts/category.html` — lọc theo category
- `posts/tag.html` — lọc theo tag
- `posts/search.html` — trang tìm kiếm
- `about.html` — trang giới thiệu
- `404.html`, `500.html` — error pages

## Features
- RSS feed: `posts/feeds.py`
- Sitemap: `posts/sitemaps.py`
- `robots.txt` phục vụ qua template

## Management Commands
- `create_post --json "<json>"` — tạo bài draft từ JSON (dùng với Claude Code)
- `export_posts` — export bài viết ra JSON
- `import_posts` — import bài viết từ JSON

## Packages
pip install django django-ckeditor django-taggit django-extensions django-import-export
pip install whitenoise psycopg2-binary python-decouple gunicorn dj-database-url
pip install mysqlclient  # chỉ local, không commit vào requirements.txt

## Design system
- Background: `#FBFBF8` (warm white)
- Dark: `#15140F`
- Accent: `oklch(0.86 0.2 125)` (lime green)
- Border: `#E8E7E0`
- Muted text: `#8A897E` / `#A8A89C`
- Font heading: Space Grotesk (700)
- Font body: Manrope (400/600)
- Font mono: JetBrains Mono — metadata, labels, tags, nav links
- Bo góc: `rounded-sm` cho buttons/chips và ảnh/cards
- Không dùng gradient
- Thumbnail: luôn dùng URL ảnh ngoài (URLField), không upload file

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
- `requirements.txt` — viết bằng Python (`pip freeze > requirements.txt`), không dùng PowerShell `>` (tránh UTF-16 BOM). Xóa `mysqlclient` trước khi commit.
- `Procfile`: `web: python manage.py collectstatic --noinput && gunicorn blog.wsgi --bind 0.0.0.0:$PORT`
- `runtime.txt`: `python-3.12.9`

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

---

## Viết bài với Claude Code

Khi user yêu cầu viết bài (ví dụ: "viết bài về Python decorators"), thực hiện theo đúng quy trình sau:

### Bước 1 — Sinh nội dung
Tạo đầy đủ các trường:
- `title`: tiêu đề rõ ràng, hấp dẫn, tiếng Việt
- `slug`: slugify từ title, dùng ký tự ASCII, không dấu (ví dụ: `python-decorators-la-gi`)
- `excerpt`: 1–2 câu tóm tắt bài, tối đa 300 ký tự
- `content`: HTML đầy đủ (xem format bên dưới)
- `meta_title`: bản rút gọn SEO của title, ≤ 70 ký tự
- `meta_description`: mô tả SEO hấp dẫn, ≤ 160 ký tự
- `tags`: 3–5 tag liên quan
- `category_name`: tên category phù hợp (nếu có trong DB)

### Bước 2 — Tạo draft trong database
Dùng management command:
```
.\venv\Scripts\python.exe manage.py create_post --json "<json_string>"
```

Hoặc dùng shell nếu cần:
```
.\venv\Scripts\python.exe manage.py shell -c "..."
```

### Bước 3 — Báo kết quả
Sau khi tạo, báo cho user:
- ID và title của bài
- Link admin để review: `/admin/posts/post/<id>/change/`

### Format nội dung HTML
- **Ngôn ngữ**: tiếng Việt, giọng chuyên nghiệp nhưng gần gũi, tránh từ sáo rỗng
- **Độ dài**: tối thiểu 600 từ, tối đa 1500 từ tùy chủ đề
- **Cấu trúc**: mở đầu hấp dẫn → thân bài 3–5 phần → kết luận có call-to-action
- **Tags HTML được dùng**: `<h2>`, `<h3>`, `<p>`, `<ul>`, `<li>`, `<ol>`, `<strong>`, `<em>`, `<blockquote>`, `<code>`, `<pre>`
- **Không dùng**: markdown, `<h1>` (đã có ở template), inline style, class
- **Code blocks**: dùng `<pre><code>...</code></pre>`
- **Blockquote**: dùng cho trích dẫn quan trọng hoặc tóm tắt ý chính

### Ví dụ cấu trúc content
```html
<p>Mở đầu hấp dẫn, đặt vấn đề hoặc câu hỏi cho người đọc...</p>

<h2>Phần 1 — Khái niệm cơ bản</h2>
<p>Giải thích...</p>

<h2>Phần 2 — Cách hoạt động</h2>
<p>Chi tiết...</p>
<pre><code>def example():
    pass</code></pre>

<h2>Phần 3 — Ứng dụng thực tế</h2>
<ul>
  <li>Điểm 1</li>
  <li>Điểm 2</li>
</ul>

<blockquote>Tóm tắt hoặc insight quan trọng nhất của bài.</blockquote>

<h2>Kết luận</h2>
<p>Tóm tắt và gợi ý bước tiếp theo...</p>
```

### Lưu ý
- `reading_time` và `views` tự tính — không cần truyền vào
- `published_at` để trống — user tự set khi publish trên admin
- Nếu category không tồn tại trong DB thì bỏ qua, đừng tạo mới
- Nếu user yêu cầu publish ngay: đặt `status='published'`, Django tự set `published_at`
- Sau khi tạo bài: **không cần build Tailwind** vì không sửa template
