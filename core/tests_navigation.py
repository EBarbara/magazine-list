from django.test import TestCase
from django.urls import reverse
from .models import Woman, Issue, Section, Appearance
from datetime import date

class NavigationLinksTests(TestCase):
    def setUp(self):
        self.woman = Woman.objects.create(name="Test Woman")
        self.issue = Issue.objects.create(publishing_date=date(2025, 1, 1), edition=1)
        self.section = Section.objects.create(name="Test Section")
        self.appearance = Appearance.objects.create(
            woman=self.woman,
            issue=self.issue,
            section=self.section
        )

    def test_issue_detail_has_woman_link(self):
        url = reverse('issue_detail', kwargs={'pk': self.issue.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        woman_detail_url = reverse('woman_detail', kwargs={'pk': self.woman.pk})
        self.assertContains(response, f'href="{woman_detail_url}"')

    def test_woman_detail_has_issue_link(self):
        url = reverse('woman_detail', kwargs={'pk': self.woman.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        issue_detail_url = reverse('issue_detail', kwargs={'pk': self.issue.pk})
        self.assertContains(response, f'href="{issue_detail_url}"')
