import unicodedata
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, FormView
from django.urls import reverse_lazy
from .models import Woman, Issue, Appearance, Section, IssueCover
from .forms import IssueForm, WomanAppearanceForm, IssueAppearanceForm, BulkAppearanceForm, IssueCoverUrlForm, IssueCoverForm
import urllib.request
from django.core.files.base import ContentFile
from datetime import date

# ... (existing imports)

class WomanAppearanceBulkCreateView(FormView):
    form_class = BulkAppearanceForm
    template_name = 'core/appearance_bulk_form.html'

    def get_success_url(self):
        return reverse_lazy('woman_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['woman'] = Woman.objects.get(pk=kwargs.get('pk') or self.kwargs['pk'])
        context['title'] = _("Bulk Add Appearances for %(woman)s") % {'woman': context['woman'].name}
        return context

    def form_valid(self, form):
        woman = Woman.objects.get(pk=self.kwargs['pk'])
        # content is now a list of dicts from clean_content
        parsed_data = form.cleaned_data['content'] 

        for data in parsed_data:
            section, _ = Section.objects.get_or_create(name=data['section_name'])
            issue, _ = Issue.objects.get_or_create(
                publishing_date=data['publishing_date'],
                edition=data['edition']
            )

            Appearance.objects.create(
                woman=woman,
                section=section,
                issue=issue
            )
            
        return super().form_valid(form)


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

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        if query:
            # Check for exact match (case-insensitive) to redirect
            exact_match = Woman.objects.filter(name__iexact=query).first()
            if exact_match:
                return redirect('woman_detail', pk=exact_match.pk)
        
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Sort in Python to handle accents correctly (SQLite limitation)
        queryset = super().get_queryset()
        
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)

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

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('covers')
        
        # Get all distinct years from the database
        # We need to list them to find prev/next/first/last
        # dates('publishing_date', 'year') returns datetime.date objects with year set
        years_date = Issue.objects.dates('publishing_date', 'year', order='ASC')
        self.years = sorted(list(set(d.year for d in years_date)))

        if not self.years:
            return queryset.none()

        # Determine current year
        year_param = self.request.GET.get('year')
        if year_param and year_param.isdigit():
            self.current_year = int(year_param)
            if self.current_year not in self.years:
                # If invalid year, fallback to first year
                 self.current_year = self.years[0]
        else:
            # Default to the first year (oldest)
            self.current_year = self.years[0]

        return queryset.filter(publishing_date__year=self.current_year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if not hasattr(self, 'years') or not self.years:
            return context

        context['current_year'] = self.current_year
        context['years'] = self.years
        
        # Navigation logic
        context['first_year'] = self.years[0]
        context['last_year'] = self.years[-1]

        # Previous/Next
        try:
            curr_index = self.years.index(self.current_year)
            context['previous_year'] = self.years[curr_index - 1] if curr_index > 0 else None
            context['next_year'] = self.years[curr_index + 1] if curr_index < len(self.years) - 1 else None
        except ValueError:
            # Should not happen as we validate current_year
            pass
            
        return context

class IssueDetailView(DetailView):
    model = Issue
    template_name = 'core/issue_detail.html'
    context_object_name = 'issue'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issue = self.object
        
        # Group appearances by section
        appearances = issue.appearance_set.select_related('woman', 'section').order_by('section__name', 'woman__name')
        
        grouped_appearances = {}
        for app in appearances:
            if app.section not in grouped_appearances:
                grouped_appearances[app.section] = []
            grouped_appearances[app.section].append(app)
            
        # Convert to list of dicts for template
        context['sections_data'] = [
            {'section': section, 'appearances': apps} 
            for section, apps in grouped_appearances.items()
        ]
        
        # Sort sections by name
        context['sections_data'].sort(key=lambda x: x['section'].name)
        
        return context

class WomanCreateView(CreateView):
    model = Woman
    fields = ['name']
    template_name = 'core/woman_form.html'

    def get_success_url(self):
        return reverse_lazy('woman_detail', kwargs={'pk': self.object.pk})

class IssueCreateView(CreateView):
    model = Issue
    form_class = IssueForm
    template_name = 'core/issue_form.html'

    def get_success_url(self):
        return reverse_lazy('issue_detail', kwargs={'pk': self.object.pk})

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
from django import forms

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

    def get_initial(self):
        initial = super().get_initial()
        # Pre-fill section if passed in GET (e.g. from the + button in a section row)
        section_id = self.request.GET.get('section_id')
        if section_id:
            try:
                section = Section.objects.get(pk=section_id)
                initial['section_name'] = section.name
            except Section.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        form.instance.issue = Issue.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['issue'] = Issue.objects.get(pk=self.kwargs['pk'])
        context['women'] = Woman.objects.all() # For datalist
        context['sections'] = Section.objects.all() # For datalist
        return context

class WomanAppearanceUpdateView(UpdateView):
    model = Appearance
    form_class = WomanAppearanceForm
    template_name = 'core/appearance_form_woman.html'
    
    def get_success_url(self):
        return reverse_lazy('woman_detail', kwargs={'pk': self.object.woman.pk})

    def get_initial(self):
        initial = super().get_initial()
        initial['section_name'] = self.object.section.name
        return initial
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['woman'] = self.object.woman
        context['sections'] = Section.objects.all() # For datalist
        context['sections'] = Section.objects.all() # For datalist
        context['title'] = _("Edit Appearance for %(woman)s") % {'woman': self.object.woman.name}
        return context

class IssueAppearanceUpdateView(UpdateView):
    model = Appearance
    form_class = IssueAppearanceForm
    template_name = 'core/appearance_form_issue.html'

    def get_success_url(self):
        return reverse_lazy('issue_detail', kwargs={'pk': self.object.issue.pk})
        
    def get_initial(self):
        initial = super().get_initial()
        initial['section_name'] = self.object.section.name
        initial['woman_name'] = self.object.woman.name
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['issue'] = self.object.issue
        context['women'] = Woman.objects.all() # For datalist
        context['sections'] = Section.objects.all() # For datalist
        context['sections'] = Section.objects.all() # For datalist
        context['title'] = _("Edit Appearance in %(issue)s") % {'issue': self.object.issue}
        return context

class AppearanceDeleteView(DeleteView):
    model = Appearance
    template_name = 'core/confirm_delete.html'
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('home')

class IssueSectionUpdateForm(forms.Form):
    section_name = forms.CharField(label='New Section Name', max_length=255, widget=forms.TextInput(attrs={'list': 'sections-list', 'class': 'form-control', 'autocomplete': 'off'}))

class IssueSectionUpdateView(FormView):
    template_name = 'core/appearance_form_issue.html' # Reuse similar template
    form_class = IssueSectionUpdateForm

    def get_success_url(self):
        return reverse_lazy('issue_detail', kwargs={'pk': self.kwargs['issue_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.issue = Issue.objects.get(pk=self.kwargs['issue_pk'])
        self.section = Section.objects.get(pk=self.kwargs['section_pk'])
        context['issue'] = self.issue
        context['issue'] = self.issue
        context['title'] = _("Update Section '%(section)s' for all appearances in %(issue)s") % {'section': self.section.name, 'issue': self.issue}
        context['sections'] = Section.objects.all() # For datalist
        # We need a flag to differentiate template behavior if needed, or just use generic title
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        section = Section.objects.get(pk=self.kwargs['section_pk'])
        initial['section_name'] = section.name
        return initial

    def form_valid(self, form):
        issue = Issue.objects.get(pk=self.kwargs['issue_pk'])
        old_section = Section.objects.get(pk=self.kwargs['section_pk'])
        new_section_name = form.cleaned_data['section_name']
        
        new_section, _ = Section.objects.get_or_create(name=new_section_name)
        
        # Update all appearances for this issue and old_section
        Appearance.objects.filter(issue=issue, section=old_section).update(section=new_section)
        
        return super().form_valid(form)

class IssueSectionDeleteView(DeleteView):
    # This is a bit tricky because DeleteView expects a single object.
    # We are deleting a group of objects. We can simulate it.
    template_name = 'core/confirm_delete.html'

    def get_object(self, queryset=None):
        # We return the Section object just to have something to render in the template confirmation
        return Section.objects.get(pk=self.kwargs['section_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issue = Issue.objects.get(pk=self.kwargs['issue_pk'])
        section = self.get_object()
        count = Appearance.objects.filter(issue=issue, section=section).count()
        count = Appearance.objects.filter(issue=issue, section=section).count()
        context['object_name'] = _("Section '%(section)s' from %(issue)s (will delete %(count)s appearances)") % {'section': section.name, 'issue': issue, 'count': count}
        context['cancel_url'] = reverse_lazy('issue_detail', kwargs={'pk': issue.pk})
        return context

    def get_success_url(self):
        return reverse_lazy('issue_detail', kwargs={'pk': self.kwargs['issue_pk']})

    def delete(self, request, *args, **kwargs):
        issue = Issue.objects.get(pk=self.kwargs['issue_pk'])
        section = self.get_object()
        Appearance.objects.filter(issue=issue, section=section).delete()
        return HttpResponseRedirect(self.get_success_url())

class IssueCoverFromUrlView(FormView):
    template_name = 'core/cover_from_url_form.html'
    form_class = IssueCoverUrlForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['issue'] = Issue.objects.get(pk=self.kwargs['issue_pk'])
        context['issue'] = Issue.objects.get(pk=self.kwargs['issue_pk'])
        context['title'] = _("Add Cover from URL for %(issue)s") % {'issue': context['issue']}
        return context

    def form_valid(self, form):
        url = form.cleaned_data['url']
        issue = Issue.objects.get(pk=self.kwargs['issue_pk'])
        
        try:
            # Download image
            req = urllib.request.Request(
                url, 
                data=None, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
                }
            )
            with urllib.request.urlopen(req) as response:
                if response.getcode() == 200:
                    image_content = response.read()
                    # Guess filename from URL or default
                    filename = url.split('/')[-1].split('?')[0]
                    if not filename:
                        filename = "cover.jpg"
                    
                    cover = IssueCover(issue=issue)
                    cover.image.save(filename, ContentFile(image_content), save=True)
                else:
                    form.add_error('url', f"Failed to download image. Status code: {response.getcode()}")
                    return self.form_invalid(form)
        except Exception as e:
            form.add_error('url', f"Error downloading image: {str(e)}")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('issue_detail', kwargs={'pk': self.kwargs['issue_pk']})

class IssueCoverCreateView(CreateView):
    model = IssueCover
    form_class = IssueCoverForm
    template_name = 'core/cover_form.html'

    def form_valid(self, form):
        form.instance.issue = Issue.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['issue'] = Issue.objects.get(pk=self.kwargs['pk'])
        context['issue'] = Issue.objects.get(pk=self.kwargs['pk'])
        context['title'] = _("Upload Cover for %(issue)s") % {'issue': context['issue']}
        return context

    def get_success_url(self):
        return reverse_lazy('issue_detail', kwargs={'pk': self.kwargs['pk']})

from django.http import HttpResponseRedirect
