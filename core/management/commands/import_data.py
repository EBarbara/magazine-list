import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Woman, Section, Issue, Appearance

class Command(BaseCommand):
    help = 'Imports data from CSV file'

    def handle(self, *args, **options):
        csv_file_path = os.path.join('As garotas da Playboy(Planilha1).csv')
        
        # Mapping for month abbreviations
        month_map = {
            'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
            'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
        }

        with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            created_appearances = 0
            
            with transaction.atomic():
                for row in reader:
                    woman_name = row['Mulher'].strip()
                    month_year = row['Mês'].strip()
                    edition_str = row['Edição'].strip()
                    section_name = row['Seção'].strip()
                    
                    if not woman_name or not month_year:
                        continue
                        
                    # Parse Date
                    try:
                        month_str, year_str = month_year.split('/')
                        month = month_map.get(month_str.lower())
                        year = int(year_str)
                        # Correction for 2-digit year
                        if year < 100:
                            year += 1900 if year > 50 else 2000
                            
                        publishing_date = datetime(year, month, 1).date()
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Invalid date format: {month_year}"))
                        continue

                    # Parse Edition
                    edition = int(edition_str) if edition_str and edition_str.isdigit() else None

                    # Get or Create Related Models
                    woman, _ = Woman.objects.get_or_create(name=woman_name)
                    section_obj, _ = Section.objects.get_or_create(name=section_name)
                    issue, _ = Issue.objects.get_or_create(
                        publishing_date=publishing_date,
                        edition=edition
                    )
                    
                    # Create Appearance
                    Appearance.objects.create(
                        woman=woman,
                        section=section_obj,
                        issue=issue
                    )
                    created_appearances += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_appearances} appearances'))
