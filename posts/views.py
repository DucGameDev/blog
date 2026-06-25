from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Post, Category


class PostListView(ListView):
    model = Post
    template_name = 'posts/index.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status=Post.STATUS_PUBLISHED).select_related('author', 'category')


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
        ).exclude(pk=self.object.pk)[:3]
        return ctx


class CategoryDetailView(ListView):
    model = Post
    template_name = 'posts/category.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            status=Post.STATUS_PUBLISHED, category=self.category
        ).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['category'] = self.category
        return ctx
