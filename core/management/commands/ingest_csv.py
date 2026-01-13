import csv
import os
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from core.models import Woman, Section, Issue, Appearance

class Command(BaseCommand):
    help = 'Ingests data from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        if not os.path.exists(csv_file_path):
            raise CommandError(f'File "{csv_file_path}" does not exist')

        self.stdout.write(self.style.SUCCESS(f'Starting ingestion from {csv_file_path}...'))

        month_map = {
            'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
            'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
        }

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            # The file uses semicolons as delimiters
            reader = csv.reader(csvfile, delimiter=';')
            HEADER = next(reader, None)  # Skip header: Mulher;Mês;Edição;Seção...

            count = 0
            for row in reader:
                if not row:
                    continue
                
                # Unpack expected columns (at least 4 are needed based on user plan)
                # usage: Mulher;Mês;Edição;Seção
                woman_name = row[0].strip()
                month_year_str = row[1].strip()
                edition_str = row[2].strip()
                section_name = row[3].strip()

                if not woman_name:
                    continue

                # Parse Date
                try:
                    month_str, year_str = month_year_str.split('/')
                    month = month_map.get(month_str.lower())
                    year = int(year_str)
                    
                    # Year pivot logic
                    if year < 100:
                        if year >= 50:
                            year += 1900
                        else:
                            year += 2000
                            
                    publishing_date = date(year, month, 1)
                except ValueError:
                    self.stdout.write(self.style.WARNING(f'Skipping row with invalid date: {month_year_str}'))
                    continue

                # Parse Edition
                edition = None
                if edition_str:
                    try:
                        edition = int(edition_str)
                    except ValueError:
                        pass # Keep None

                # Create/Get Models
                woman, _ = Woman.objects.get_or_create(name=woman_name)
                
                section, _ = Section.objects.get_or_create(name=section_name)

                issue, _ = Issue.objects.get_or_create(
                    publishing_date=publishing_date,
                    edition=edition
                )

                Appearance.objects.create(
                    woman=woman,
                    section=section,
                    issue=issue
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully ingested {count} appearances'))
