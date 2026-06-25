from django.urls import path
from . import views
from .feeds import LatestPostsFeed

app_name = 'posts'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('tag/<slug:slug>/', views.TagListView.as_view(), name='tag'),
    path('newsletter/', views.newsletter_subscribe, name='newsletter'),
    path('comment/<slug:slug>/', views.submit_comment, name='comment'),
    path('rss/', LatestPostsFeed(), name='rss'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category'),
    path('<slug:slug>/', views.PostDetailView.as_view(), name='detail'),
]
