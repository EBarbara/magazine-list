from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('woman/', views.WomanListView.as_view(), name='woman_list'),
    path('woman/new/', views.WomanCreateView.as_view(), name='woman_create'),
    path('woman/<int:pk>/', views.WomanDetailView.as_view(), name='woman_detail'),
    path('woman/<int:pk>/delete/', views.WomanDeleteView.as_view(), name='woman_delete'),
    path('issue/', views.IssueListView.as_view(), name='issue_list'),
    path('issue/new/', views.IssueCreateView.as_view(), name='issue_create'),
    path('issue/<int:pk>/', views.IssueDetailView.as_view(), name='issue_detail'),
    path('issue/<int:pk>/delete/', views.IssueDeleteView.as_view(), name='issue_delete'),
    path('woman/<int:pk>/appearance/new/', views.WomanAppearanceCreateView.as_view(), name='woman_appearance_create'),
    path('issue/<int:pk>/appearance/new/', views.IssueAppearanceCreateView.as_view(), name='issue_appearance_create'),
    path('appearance/<int:pk>/delete/', views.AppearanceDeleteView.as_view(), name='appearance_delete'),
    path('appearance/<int:pk>/edit/woman/', views.WomanAppearanceUpdateView.as_view(), name='woman_appearance_edit'),
    path('appearance/<int:pk>/edit/issue/', views.IssueAppearanceUpdateView.as_view(), name='issue_appearance_edit'),
]
