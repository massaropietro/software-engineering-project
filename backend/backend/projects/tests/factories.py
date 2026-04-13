import factory
from factory.django import DjangoModelFactory

from backend.projects.models import MutationAnalysis, MutationResult, Project


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.LazyAttribute(lambda o: f"Project {Project.objects.count() + 1}")
    description = factory.LazyAttribute(
        lambda o: f"Description {Project.objects.count() + 1}"
    )
    zip_file = None
    repo_url = factory.Faker("url")


class MutationAnalysisFactory(DjangoModelFactory):
    class Meta:
        model = MutationAnalysis

    project = factory.SubFactory(ProjectFactory)
    files = factory.LazyFunction(lambda: ["main.py"])
    language = "python"
    status = "pending"


class MutationResultFactory(DjangoModelFactory):
    class Meta:
        model = MutationResult

    analysis = factory.SubFactory(MutationAnalysisFactory)
    file = "main.py"
    mutant_id = factory.Sequence(lambda n: str(n + 1))
    status = "survived"
    line = factory.Faker("random_int", min=1, max=200)
    description = ""
