import unicodedata
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from .models import Woman, Issue, Appearance, Section
from .forms import IssueForm, WomanAppearanceForm, IssueAppearanceForm

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

class WomanCreateView(CreateView):
    model = Woman
    fields = ['name']
    template_name = 'core/woman_form.html'
    success_url = reverse_lazy('woman_list')

class IssueCreateView(CreateView):
    model = Issue
    form_class = IssueForm
    template_name = 'core/issue_form.html'
    success_url = reverse_lazy('issue_list')

class WomanDeleteView(DeleteView):
    model = Woman
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('woman_list')

class IssueDeleteView(DeleteView):
    model = Issue
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('issue_list')

from .forms import WomanAppearanceForm, IssueAppearanceForm
from .models import Appearance, Section

class WomanAppearanceCreateView(CreateView):
    model = Appearance
    form_class = WomanAppearanceForm
    template_name = 'core/appearance_form_woman.html'
    
    def get_success_url(self):
        return reverse_lazy('woman_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        form.instance.woman = Woman.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['woman'] = Woman.objects.get(pk=self.kwargs['pk'])
        context['sections'] = Section.objects.all() # For datalist
        return context

class IssueAppearanceCreateView(CreateView):
    model = Appearance
    form_class = IssueAppearanceForm
    template_name = 'core/appearance_form_issue.html'

    def get_success_url(self):
        return reverse_lazy('issue_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        form.instance.issue = Issue.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['issue'] = Issue.objects.get(pk=self.kwargs['pk'])
        context['women'] = Woman.objects.all() # For datalist
        context['sections'] = Section.objects.all() # For datalist
        return context

class AppearanceDeleteView(DeleteView):
    model = Appearance
    template_name = 'core/confirm_delete.html'
    
    def get_success_url(self):
        # We want to go back to where we came from (Woman Detail or Issue Detail)
        # Check if ?next= is in the request (passed from template)
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
            
        # Fallback based on specific logic if next isn't present
        # If we have a woman context (unlikely to know purely from appearance deletion unless we check relations)
        # But actually, deleting the object removes the relation, so self.object might be gone by the time we check?
        # DeleteView calls delete() which calls get_success_url() AFTER?
        # Wait, delete() calls get_success_url() *then* deletes? No.
        # Standard DeleteView implementation:
        # def delete(self, request, *args, **kwargs):
        #     self.object = self.get_object()
        #     success_url = self.get_success_url()
        #     self.object.delete()
        #     return HttpResponseRedirect(success_url)
        # So self.object exists when get_success_url is called!
        
        if self.object.woman:
             # Default fallback might be Woman List or Issue List?
             # Let's try to infer interesting context, or just default to home.
             pass
             
        return reverse_lazy('home')
