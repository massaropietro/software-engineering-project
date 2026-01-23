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


class ProjectFileFactory(DjangoModelFactory):
    class Meta:
        model = "projects.ProjectFile"

    project = factory.SubFactory(ProjectFactory)
    path = factory.Faker("file_path")
    content = factory.Faker("text")
    size = factory.Faker("random_int", min=10, max=1000)
