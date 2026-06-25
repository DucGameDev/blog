from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Post


class LatestPostsFeed(Feed):
    title = 'ducdev'
    link = '/'
    description = 'Bài viết mới nhất từ ducdev'

    def items(self):
        return Post.objects.filter(status=Post.STATUS_PUBLISHED).order_by('-published_at')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or item.meta_description

    def item_pubdate(self, item):
        return item.published_at

    def item_link(self, item):
        return reverse('posts:detail', kwargs={'slug': item.slug})
