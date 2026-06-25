import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from posts.models import Post


class Command(BaseCommand):
    help = 'Export posts to a portable JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output', '-o',
            default='posts_export.json',
            help='Output file path (default: posts_export.json)',
        )
        parser.add_argument(
            '--status',
            choices=['draft', 'published', 'all'],
            default='all',
            help='Filter by status (default: all)',
        )

    def handle(self, *args, **options):
        qs = Post.objects.select_related('author', 'category').prefetch_related('tags')
        if options['status'] != 'all':
            qs = qs.filter(status=options['status'])

        data = []
        for post in qs.order_by('id'):
            published_at = None
            if post.published_at:
                if timezone.is_aware(post.published_at):
                    published_at = post.published_at.isoformat()
                else:
                    published_at = timezone.make_aware(post.published_at).isoformat()

            data.append({
                'title': post.title,
                'slug': post.slug,
                'excerpt': post.excerpt,
                'content': post.content,
                'status': post.status,
                'published_at': published_at,
                'reading_time': post.reading_time,
                'views': post.views,
                'meta_title': post.meta_title,
                'meta_description': post.meta_description,
                'note': post.note,
                'author_username': post.author.username,
                'category_name': post.category.name if post.category else None,
                'tags': [t.name for t in post.tags.all()],
            })

        out_path = Path(options['output'])
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

        self.stdout.write(self.style.SUCCESS(
            f'Exported {len(data)} posts → {out_path.resolve()}'
        ))
