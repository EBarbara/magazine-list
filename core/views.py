from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Woman

def home(request):
    return render(request, 'core/home.html')

class WomanListView(ListView):
    model = Woman
    template_name = 'core/woman_list.html'
    context_object_name = 'women'
    ordering = ['name']

class WomanDetailView(DetailView):
    model = Woman
    template_name = 'core/woman_detail.html'
    context_object_name = 'woman'
