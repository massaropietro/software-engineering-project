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


def test_file_content_url():
    url = "/api/projects/some-uuid/file_content/"
    assert reverse("api:projects-file-content", kwargs={"pk": "some-uuid"}) == url
    assert resolve(url).view_name == "api:projects-file-content"


def test_analyses_list_url():
    assert reverse("api:analyses-list") == "/api/analyses/"
    assert resolve("/api/analyses/").view_name == "api:analyses-list"


def test_analyses_detail_url():
    assert reverse("api:analyses-detail", kwargs={"pk": "some-uuid"}) == "/api/analyses/some-uuid/"
    assert resolve("/api/analyses/some-uuid/").view_name == "api:analyses-detail"


def test_analyses_retry_url():
    url = "/api/analyses/some-uuid/retry/"
    assert reverse("api:analyses-retry", kwargs={"pk": "some-uuid"}) == url
    assert resolve(url).view_name == "api:analyses-retry"


def test_mutation_results_list_url():
    assert reverse("api:mutation-results-list") == "/api/mutation-results/"
    assert resolve("/api/mutation-results/").view_name == "api:mutation-results-list"
