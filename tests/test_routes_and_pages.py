import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("url_name", "expected_path"),
    (
        ("pages:index", "/"),
        ("pages:about", "/about/"),
        ("pages:rules", "/rules/"),
        ("catalog:catalog_list", "/catalog/"),
    ),
)
def test_named_routes(url_name, expected_path):
    assert reverse(url_name) == expected_path, (
        f"Маршрут {url_name} должен иметь адрес {expected_path}"
    )


def test_product_detail_named_route():
    assert reverse("catalog:product_detail", args=(7,)) == "/catalog/7/"


@pytest.mark.parametrize(
    ("url", "template_name"),
    (
        ("/", "pages/index.html"),
        ("/about/", "pages/about.html"),
        ("/rules/", "pages/rules.html"),
        ("/catalog/", "catalog/catalog_list.html"),
    ),
)
def test_page_uses_expected_template(client, url, template_name):
    response = client.get(url)
    assert response.status_code == 200, f"Страница {url} должна возвращать код 200"
    used = {template.name for template in response.templates if template.name}
    assert template_name in used, (
        f"Страница {url} должна использовать шаблон {template_name}"
    )
    assert "base.html" in used, f"Шаблон страницы {url} должен наследовать base.html"


def test_unknown_product_still_returns_404(client):
    unknown_id = 987654321
    response = client.get(reverse("catalog:product_detail", args=(unknown_id,)))
    assert response.status_code == 404, "Неизвестный товар должен возвращать код 404"
