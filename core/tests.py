from django.test import TestCase
from django.urls import reverse
from .models import Woman, Issue
from datetime import date

class CreationRedirectTests(TestCase):
    def test_woman_create_redirects_to_detail(self):
        url = reverse('woman_create')
        data = {'name': 'New Woman'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) # Redirect
        
        woman = Woman.objects.get(name='New Woman')
        expected_url = reverse('woman_detail', kwargs={'pk': woman.pk})
        self.assertRedirects(response, expected_url)

    def test_issue_create_redirects_to_detail(self):
        url = reverse('issue_create')
        data = {'publishing_date': '2025-01', 'edition': 1} # Format YYYY-MM based on logic
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) # Redirect
        
        issue = Issue.objects.get(publishing_date=date(2025, 1, 1), edition=1)
        expected_url = reverse('issue_detail', kwargs={'pk': issue.pk})
        self.assertRedirects(response, expected_url)
