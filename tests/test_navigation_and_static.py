from html.parser import HTMLParser

import pytest
from django.contrib.staticfiles import finders
from django.urls import reverse

pytestmark = pytest.mark.django_db


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.stylesheets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        href = attrs.get("href")
        if tag == "a" and href:
            self.hrefs.append(href)
        if tag == "link" and href and "stylesheet" in attrs.get("rel", "").lower():
            self.stylesheets.append(href)


@pytest.mark.parametrize("url", ("/", "/about/", "/rules/", "/catalog/"))
def test_base_navigation_is_present_on_pages(client, url):
    response = client.get(url)
    parser = LinkParser()
    parser.feed(response.content.decode(response.charset or "utf-8"))

    expected = {
        reverse("pages:index"),
        reverse("pages:about"),
        reverse("pages:rules"),
        reverse("catalog:catalog_list"),
    }
    assert expected.issubset(set(parser.hrefs)), (
        "В общей навигации нужны ссылки на главную, about, rules и каталог"
    )


def test_css_file_is_discoverable_by_django():
    found = finders.find("css/style.css")
    assert found, "Django не находит static/css/style.css"


def test_css_is_linked_from_base_template(client):
    response = client.get("/")
    parser = LinkParser()
    parser.feed(response.content.decode(response.charset or "utf-8"))
    assert any(href.endswith("css/style.css") for href in parser.stylesheets), (
        "Подключите css/style.css в base.html через тег static"
    )
