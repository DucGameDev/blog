from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.urls import reverse
from .models import Post, Category, Subscriber, Comment


class PostListView(ListView):
    model = Post
    template_name = 'posts/index.html'
    context_object_name = 'posts'
    paginate_by = 6

    def _published(self):
        return Post.objects.filter(status=Post.STATUS_PUBLISHED).select_related('author', 'category')

    def get_queryset(self):
        qs = self._published()
        featured = qs.first()
        if featured:
            return qs.exclude(pk=featured.pk)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['featured'] = self._published().first()
        return ctx


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(status=Post.STATUS_PUBLISHED).select_related('author', 'category')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Post.objects.filter(pk=obj.pk).update(views=obj.views + 1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['related_posts'] = Post.objects.filter(
            status=Post.STATUS_PUBLISHED,
            category=self.object.category,
        ).exclude(pk=self.object.pk).select_related('author', 'category')[:3]
        ctx['comments'] = self.object.comments.filter(approved=True)
        ctx['comment_count'] = ctx['comments'].count()

        published = list(
            Post.objects.filter(status=Post.STATUS_PUBLISHED)
            .order_by('published_at')
            .values_list('pk', flat=True)
        )
        try:
            idx = published.index(self.object.pk)
            ctx['prev_post'] = Post.objects.filter(pk=published[idx - 1]).first() if idx > 0 else None
            ctx['next_post'] = Post.objects.filter(pk=published[idx + 1]).first() if idx < len(published) - 1 else None
        except ValueError:
            ctx['prev_post'] = None
            ctx['next_post'] = None

        return ctx


class CategoryDetailView(ListView):
    model = Post
    template_name = 'posts/category.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            status=Post.STATUS_PUBLISHED, category=self.category
        ).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['category'] = self.category
        return ctx


class TagListView(ListView):
    template_name = 'posts/tag.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        self.tag_slug = self.kwargs['slug']
        return Post.objects.filter(
            status=Post.STATUS_PUBLISHED,
            tags__slug=self.tag_slug,
        ).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tag_slug'] = self.tag_slug
        return ctx


class SearchView(ListView):
    template_name = 'posts/search.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        q = self.request.GET.get('q', '').strip()
        if not q:
            return Post.objects.none()
        return Post.objects.filter(
            status=Post.STATUS_PUBLISHED
        ).filter(
            Q(title__icontains=q) | Q(excerpt__icontains=q)
        ).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class AboutView(TemplateView):
    template_name = 'about.html'


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if '@' in email:
            Subscriber.objects.get_or_create(email=email)
    return redirect(request.META.get('HTTP_REFERER', '/'))


def submit_comment(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(Post, slug=slug, status=Post.STATUS_PUBLISHED)
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        content = request.POST.get('content', '').strip()
        if name and email and content and '@' in email:
            Comment.objects.create(post=post, name=name, email=email, content=content)
    return redirect(reverse('posts:detail', kwargs={'slug': slug}) + '#comments')
