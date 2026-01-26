from django.test import TestCase, Client
from django.urls import reverse
from core.models import Issue
from datetime import date

class IssuePaginationTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create issues in different years
        years = [1975, 1976, 1978, 1980] # Gap in 1977, 1979
        for year in years:
            for month in range(1, 4): # Create 3 issues per year
                Issue.objects.create(publishing_date=date(year, month, 1), edition=year*100+month)

    def test_default_view_shows_first_year(self):
        response = self.client.get(reverse('issue_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_year'], 1975)
        self.assertEqual(len(response.context['issues']), 3)
        self.assertEqual(response.context['first_year'], 1975)
        self.assertEqual(response.context['last_year'], 1980)
        self.assertIsNone(response.context['previous_year'])
        self.assertEqual(response.context['next_year'], 1976)

    def test_specific_year_view(self):
        response = self.client.get(reverse('issue_list'), {'year': 1978})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_year'], 1978)
        self.assertEqual(len(response.context['issues']), 3)
        self.assertEqual(response.context['previous_year'], 1976) # Check gap handling
        self.assertEqual(response.context['next_year'], 1980)

    def test_invalid_year_fallback(self):
        response = self.client.get(reverse('issue_list'), {'year': 2050})
        self.assertEqual(response.status_code, 200)
        # Should fallback to first year (1975)
        self.assertEqual(response.context['current_year'], 1975)

    def test_last_year_navigation(self):
        response = self.client.get(reverse('issue_list'), {'year': 1980})
        self.assertEqual(response.context['current_year'], 1980)
        self.assertEqual(response.context['previous_year'], 1978)
        self.assertIsNone(response.context['next_year'])
