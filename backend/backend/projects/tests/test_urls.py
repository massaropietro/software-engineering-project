from django.urls import reverse, resolve


def test_project_list_url():
    assert reverse("api:projects-list") == "/api/projects/"
    assert resolve("/api/projects/").view_name == "api:projects-list"


def test_project_detail_url():
    assert (
        reverse("api:projects-detail", kwargs={"pk": "some-uuid"})
        == "/api/projects/some-uuid/"
    )
    assert resolve("/api/projects/some-uuid/").view_name == "api:projects-detail"


def test_retry_build_url():
    url = "/api/projects/some-uuid/retry_build_filesystem/"
    assert reverse("api:projects-retry-build-filesystem", kwargs={"pk": "some-uuid"}) == url
    assert resolve(url).view_name == "api:projects-retry-build-filesystem"
