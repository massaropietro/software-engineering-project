import factory
from factory.django import DjangoModelFactory
from backend.projects.models import Project

class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"Project {n}")
    description = factory.Sequence(lambda n: f"Description {n}")
    zip_file = None
    repo_url = factory.Faker("url")

