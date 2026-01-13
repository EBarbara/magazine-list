import unicodedata
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Woman, Issue

def home(request):
    return render(request, 'core/home.html')

def normalize_text(text):
    if not text:
        return ""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower()

class WomanListView(ListView):
    model = Woman
    template_name = 'core/woman_list.html'
    context_object_name = 'women'
    paginate_by = 20

    def get_queryset(self):
        # Sort in Python to handle accents correctly (SQLite limitation)
        queryset = super().get_queryset()
        return sorted(queryset, key=lambda w: normalize_text(w.name))

class WomanDetailView(DetailView):
    model = Woman
    template_name = 'core/woman_detail.html'
    context_object_name = 'woman'

class IssueListView(ListView):
    model = Issue
    template_name = 'core/issue_list.html'
    context_object_name = 'issues'
    ordering = ['publishing_date']
    paginate_by = 20

class IssueDetailView(DetailView):
    model = Issue
    template_name = 'core/issue_detail.html'
    context_object_name = 'issue'
