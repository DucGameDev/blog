from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Post, Category


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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['related_posts'] = Post.objects.filter(
            status=Post.STATUS_PUBLISHED,
            category=self.object.category,
        ).exclude(pk=self.object.pk).select_related('author', 'category')[:3]
        return ctx


class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/index.html'
    context_object_name = 'posts'
    paginate_by = 20
    login_url = '/admin/login/'

    def get_queryset(self):
        qs = Post.objects.select_related('author', 'category').order_by('-created_at')
        status = self.request.GET.get('status', '')
        q = self.request.GET.get('q', '')
        if status in [Post.STATUS_PUBLISHED, Post.STATUS_DRAFT]:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(title__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['stats'] = {
            'published': Post.objects.filter(status=Post.STATUS_PUBLISHED).count(),
            'draft': Post.objects.filter(status=Post.STATUS_DRAFT).count(),
            'total': Post.objects.count(),
            'categories': Category.objects.count(),
            'authors': User.objects.filter(posts__isnull=False).distinct().count(),
        }
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['search_q'] = self.request.GET.get('q', '')
        ctx['active_nav'] = 'posts'
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
