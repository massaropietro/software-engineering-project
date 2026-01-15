from django.core.management.base import BaseCommand
from backend.projects.tests.factories import ProjectFactory

class Command(BaseCommand):
    help = 'Seeds the database with random projects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            type=int,
            default=10,
            help='Number of projects to create',
        )

    def handle(self, *args, **options):
        number = options['number']
        self.stdout.write(f'Creating {number} projects...')

        try:
            ProjectFactory.create_batch(number)
            self.stdout.write(self.style.SUCCESS(f'Successfully created {number} projects'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating projects: {str(e)}'))
