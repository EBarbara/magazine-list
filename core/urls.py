from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('woman/', views.WomanListView.as_view(), name='woman_list'),
    path('woman/<int:pk>/', views.WomanDetailView.as_view(), name='woman_detail'),
    path('issue/', views.IssueListView.as_view(), name='issue_list'),
    path('issue/<int:pk>/', views.IssueDetailView.as_view(), name='issue_detail'),
]
