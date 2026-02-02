from django import forms
from .models import Issue, Appearance, IssueCover
from datetime import date
from django.utils.translation import gettext_lazy as _

class BulkAppearanceForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'placeholder': _('jan/90; 1; Capa\nfev/95; ; Entrevista')}),
        help_text=_("Format: Month/Year; Edition; Section")
    )

    def clean_content(self):
        content = self.cleaned_data['content']
        lines = content.split('\n')
        parsed_data = []
        errors = []
        
        month_map = {
            'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
            'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
        }

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(';')
            if len(parts) < 3:
                errors.append(f"Line {i+1}: Invalid format (expected 'Month/Year; Edition; Section')")
                continue
                
            month_year_str = parts[0].strip()
            edition_str = parts[1].strip()
            section_name = parts[2].strip()

            # Parse Date
            try:
                if '/' not in month_year_str:
                     raise ValueError("Missing '/'")
                month_str, year_str = month_year_str.split('/')
                month = month_map.get(month_str.lower())
                if not month:
                    raise ValueError(f"Invalid month '{month_str}'")
                year = int(year_str)
                
                if year < 100:
                    if year >= 50:
                        year += 1900
                    else:
                        year += 2000
                        
                publishing_date = date(year, month, 1)
            except (ValueError, IndexError):
                errors.append(f"Line {i+1}: Invalid date '{month_year_str}'")
                continue

            # Parse Edition
            edition = None
            if edition_str:
                try:
                    edition = int(edition_str)
                except ValueError:
                    errors.append(f"Line {i+1}: Invalid edition '{edition_str}'")
                    continue
            
            parsed_data.append({
                'publishing_date': publishing_date,
                'edition': edition,
                'section_name': section_name
            })
            
        if errors:
            raise forms.ValidationError(errors)
            
        return parsed_data

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['publishing_date', 'edition']
        widgets = {
            'publishing_date': forms.DateInput(attrs={'type': 'month'}, format='%Y-%m'),
        }

    publishing_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month'}, format='%Y-%m'),
        input_formats=['%Y-%m'],
    )

    def clean(self):
        cleaned_data = super().clean()
        publishing_date = cleaned_data.get('publishing_date')
        edition = cleaned_data.get('edition')

        if publishing_date:
            # Check for duplicates, handling NULL edition specifically for SQLite
            query = Issue.objects.filter(publishing_date=publishing_date)
            
            if edition is None:
                query = query.filter(edition__isnull=True)
            else:
                query = query.filter(edition=edition)

            if query.exists():
                raise forms.ValidationError(_("Issue with this Publishing Date and Edition already exists."))
        
        return cleaned_data

class WomanAppearanceForm(forms.ModelForm):
    # Field to select existing issue
    issue = forms.ModelChoiceField(
        queryset=Issue.objects.all().order_by('publishing_date'),
        required=False,
        label=_("Existing Issue")
    )
    
    # Fields to create a NEW issue
    new_issue_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'month'}, format='%Y-%m'),
        input_formats=['%Y-%m'],
        label=_("Or New Issue Date")
    )
    new_issue_edition = forms.IntegerField(required=False, label=_("Edition (Optional)"))

    # Field for Section (Choose or Create)
    section_name = forms.CharField(label=_("Section"), widget=forms.TextInput(attrs={'list': 'sections-list'}))

    class Meta:
        model = Appearance
        fields = ['issue', 'section_name'] # We treat section_name as a pseudo-field here

    def clean(self):
        cleaned_data = super().clean()
        issue = cleaned_data.get('issue')
        new_issue_date = cleaned_data.get('new_issue_date')
        
        if not issue and not new_issue_date:
            raise forms.ValidationError(_("You must select an existing issue OR provide a date for a new one."))
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle Section
        section_name = self.cleaned_data.get('section_name')
        from .models import Section
        section, _ = Section.objects.get_or_create(name=section_name)
        instance.section = section
        
        # Handle Issue
        issue = self.cleaned_data.get('issue')
        if not issue:
            new_issue_date = self.cleaned_data.get('new_issue_date')
            new_issue_edition = self.cleaned_data.get('new_issue_edition')
            # Check if this issue already exists to avoid duplicates
            existing_issue_query = Issue.objects.filter(publishing_date=new_issue_date)
            if new_issue_edition is None:
                 existing_issue_query = existing_issue_query.filter(edition__isnull=True)
            else:
                 existing_issue_query = existing_issue_query.filter(edition=new_issue_edition)
            
            if existing_issue_query.exists():
                issue = existing_issue_query.first()
            else:
                issue = Issue.objects.create(publishing_date=new_issue_date, edition=new_issue_edition)
        
        instance.issue = issue
        
        if commit:
            instance.save()
        return instance

class IssueAppearanceForm(forms.ModelForm):
    # Field for Woman (Choose or Create)
    woman_name = forms.CharField(label=_("Woman"), widget=forms.TextInput(attrs={'list': 'women-list'}))
    
    # Field for Section (Choose or Create)
    section_name = forms.CharField(label=_("Section"), widget=forms.TextInput(attrs={'list': 'sections-list'}))

    class Meta:
        model = Appearance
        fields = ['woman_name', 'section_name']

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle Woman
        woman_name = self.cleaned_data.get('woman_name')
        from .models import Woman
        woman, _ = Woman.objects.get_or_create(name=woman_name)
        instance.woman = woman
        
        # Handle Section
        section_name = self.cleaned_data.get('section_name')
        from .models import Section
        section, _ = Section.objects.get_or_create(name=section_name)
        instance.section = section
        
        if commit:
            instance.save()
        return instance

class IssueCoverUrlForm(forms.Form):
    url = forms.URLField(label=_("Image URL"), required=True, widget=forms.TextInput(attrs={'placeholder': 'https://example.com/image.jpg'}))

class IssueCoverForm(forms.ModelForm):
    class Meta:
        model = IssueCover
        fields = ['image']
