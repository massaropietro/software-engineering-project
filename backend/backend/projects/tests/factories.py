import factory
from factory.django import DjangoModelFactory
from backend.projects.models import Project


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.LazyAttribute(lambda o: f"Project {Project.objects.count() + 1}")
    description = factory.LazyAttribute(
        lambda o: f"Description {Project.objects.count() + 1}"
    )
    zip_file = None
    repo_url = factory.Faker("url")
