import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils.text import slugify
from posts.models import Post, Category


class Command(BaseCommand):
    help = 'Create a draft post from JSON. Used by Claude Code.'

    def add_arguments(self, parser):
        parser.add_argument('--json', type=str, required=True, help='JSON string with post data')
        parser.add_argument('--publish', action='store_true', help='Publish immediately (default: draft)')
        parser.add_argument('--author', type=str, default='', help='Author username (default: first superuser)')

    def handle(self, *args, **options):
        try:
            data = json.loads(options['json'])
        except json.JSONDecodeError as e:
            raise CommandError(f'JSON không hợp lệ: {e}')

        title = data.get('title', '').strip()
        if not title:
            raise CommandError('Thiếu trường "title"')

        content = data.get('content', '').strip()
        if not content:
            raise CommandError('Thiếu trường "content"')

        username = options['author']
        if username:
            try:
                author = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'Không tìm thấy user: {username}')
        else:
            author = User.objects.filter(is_superuser=True).first()
            if not author:
                author = User.objects.first()
            if not author:
                raise CommandError('Không có user nào trong database. Chạy createsuperuser trước.')

        slug = data.get('slug', '') or slugify(title)
        if Post.objects.filter(slug=slug).exists():
            base = slug
            i = 2
            while Post.objects.filter(slug=f'{base}-{i}').exists():
                i += 1
            slug = f'{base}-{i}'

        category = None
        category_name = data.get('category_name', '').strip()
        if category_name:
            category = Category.objects.filter(name__iexact=category_name).first()

        status = Post.STATUS_PUBLISHED if options['publish'] else Post.STATUS_DRAFT

        post = Post(
            title=title,
            slug=slug,
            excerpt=data.get('excerpt', '')[:500],
            content=content,
            meta_title=data.get('meta_title', '')[:70],
            meta_description=data.get('meta_description', '')[:160],
            author=author,
            category=category,
            status=status,
        )
        post.save()

        tags = data.get('tags', [])
        if isinstance(tags, list) and tags:
            post.tags.add(*[str(t).strip() for t in tags if str(t).strip()])

        admin_url = f'/admin/posts/post/{post.pk}/change/'
        self.stdout.write(self.style.SUCCESS(
            f'\nPost created!\n'
            f'  ID     : {post.pk}\n'
            f'  Title  : {post.title}\n'
            f'  Slug   : {post.slug}\n'
            f'  Status : {post.status}\n'
            f'  Author : {author.username}\n'
            f'  Admin  : {admin_url}\n'
        ))
