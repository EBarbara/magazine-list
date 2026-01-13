from django import forms
from .models import Issue, Appearance

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
                raise forms.ValidationError("Issue with this Publishing Date and Edition already exists.")
        
        return cleaned_data

class WomanAppearanceForm(forms.ModelForm):
    # Field to select existing issue
    issue = forms.ModelChoiceField(
        queryset=Issue.objects.all().order_by('publishing_date'),
        required=False,
        label="Existing Issue"
    )
    
    # Fields to create a NEW issue
    new_issue_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'month'}, format='%Y-%m'),
        input_formats=['%Y-%m'],
        label="Or New Issue Date"
    )
    new_issue_edition = forms.IntegerField(required=False, label="Edition (Optional)")

    # Field for Section (Choose or Create)
    section_name = forms.CharField(label="Section", widget=forms.TextInput(attrs={'list': 'sections-list'}))

    class Meta:
        model = Appearance
        fields = ['issue', 'section_name'] # We treat section_name as a pseudo-field here

    def clean(self):
        cleaned_data = super().clean()
        issue = cleaned_data.get('issue')
        new_issue_date = cleaned_data.get('new_issue_date')
        
        if not issue and not new_issue_date:
            raise forms.ValidationError("You must select an existing issue OR provide a date for a new one.")
        
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
    woman_name = forms.CharField(label="Woman", widget=forms.TextInput(attrs={'list': 'women-list'}))
    
    # Field for Section (Choose or Create)
    section_name = forms.CharField(label="Section", widget=forms.TextInput(attrs={'list': 'sections-list'}))

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
