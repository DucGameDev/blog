import json
from pathlib import Path
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from posts.models import Category, Post


class Command(BaseCommand):
    help = 'Import posts from a JSON file exported by export_posts'

    def add_arguments(self, parser):
        parser.add_argument(
            'input',
            help='Path to JSON file produced by export_posts',
        )
        parser.add_argument(
            '--author',
            default=None,
            help='Override author username for all imported posts',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing posts (matched by slug). Default: skip duplicates.',
        )

    def handle(self, *args, **options):
        in_path = Path(options['input'])
        if not in_path.exists():
            raise CommandError(f'File not found: {in_path}')

        data = json.loads(in_path.read_text(encoding='utf-8'))

        # Resolve override author
        override_author = None
        if options['author']:
            try:
                override_author = User.objects.get(username=options['author'])
            except User.DoesNotExist:
                raise CommandError(f"User '{options['author']}' not found.")

        created = updated = skipped = 0

        for item in data:
            slug = item['slug']
            exists = Post.objects.filter(slug=slug).exists()

            if exists and not options['update']:
                self.stdout.write(f'  SKIP (exists): {slug}')
                skipped += 1
                continue

            # Resolve author
            author = override_author
            if not author:
                try:
                    author = User.objects.get(username=item['author_username'])
                except User.DoesNotExist:
                    # Fall back to first superuser
                    author = User.objects.filter(is_superuser=True).first()
                    if not author:
                        author = User.objects.first()
                    self.stdout.write(self.style.WARNING(
                        f"  Author '{item['author_username']}' not found, using '{author}'"
                    ))

            # Resolve category
            category = None
            if item.get('category_name'):
                category = Category.objects.filter(name=item['category_name']).first()
                if not category:
                    self.stdout.write(self.style.WARNING(
                        f"  Category '{item['category_name']}' not found, leaving null"
                    ))

            # Parse published_at
            published_at = None
            if item.get('published_at'):
                published_at = parse_datetime(item['published_at'])
                if published_at and timezone.is_naive(published_at):
                    published_at = timezone.make_aware(published_at)

            fields = dict(
                title=item['title'],
                excerpt=item.get('excerpt', ''),
                content=item.get('content', ''),
                status=item.get('status', 'draft'),
                published_at=published_at,
                reading_time=item.get('reading_time', 1),
                views=item.get('views', 0),
                meta_title=item.get('meta_title', ''),
                meta_description=item.get('meta_description', ''),
                note=item.get('note', ''),
                author=author,
                category=category,
            )

            if exists:
                Post.objects.filter(slug=slug).update(**fields)
                post = Post.objects.get(slug=slug)
                updated += 1
                label = 'UPDATE'
            else:
                post = Post.objects.create(slug=slug, **fields)
                created += 1
                label = 'CREATE'

            # Tags
            post.tags.set(*item.get('tags', []))

            self.stdout.write(f'  {label}: {slug}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone — created: {created}, updated: {updated}, skipped: {skipped}'
        ))
