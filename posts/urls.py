from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category'),
    path('<slug:slug>/', views.PostDetailView.as_view(), name='detail'),
]
