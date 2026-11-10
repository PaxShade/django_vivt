import pytest
from html.parser import HTMLParser
from django.urls import reverse

from .test_navigation_and_static import LinkParser

pytestmark = pytest.mark.django_db


def test_catalog_gets_all_model_objects_in_id_order(client, Product, product_factory):
    Product.objects.all().delete()
    # Порядок создания и названий специально отличается от порядка id.
    third = product_factory(pk=91, name="Альфа", is_available=False)
    first = product_factory(pk=17, name="Янтарь")
    second = product_factory(pk=43, name="Маяк")
    response = client.get(reverse("catalog:catalog_list"))
    assert response.status_code == 200
    products = list(response.context["products"])
    assert all(isinstance(obj, Product) for obj in products), (
        "В products нужны объекты Product из базы данных"
    )
    assert [obj.pk for obj in products] == [first.pk, second.pk, third.pk], (
        "Покажите все товары, включая отсутствующие, по возрастанию id"
    )
    text = response.content.decode(response.charset)
    parser = LinkParser()
    parser.feed(text)
    for product in (first, second, third):
        assert product.name in text
        assert reverse("catalog:product_detail", args=(product.pk,)) in parser.hrefs
    assert text.index(first.name) < text.index(second.name) < text.index(third.name)


def test_detail_context_contains_selected_model(client, product_factory, Product):
    product_factory(pk=17, name="Другой товар")
    selected = product_factory(pk=84, name="Выбранный товар", description="Особое описание")
    response = client.get(reverse("catalog:product_detail", args=(selected.pk,)))
    assert response.status_code == 200
    assert isinstance(response.context["product"], Product)
    assert response.context["product"].pk == selected.pk
    used = {t.name for t in response.templates if t.name}
    assert {"base.html", "catalog/product_detail.html"}.issubset(used)
    text = response.content.decode(response.charset)
    assert selected.name in text and selected.description in text
    assert str(selected.pk) in text, "Покажите идентификатор товара"
    # Django может локализовать разделитель и группировать разряды.
    compact = text.replace("\xa0", "").replace("\u202f", "").replace(" ", "")
    assert "1234.50" in compact or "1234,50" in compact, "Покажите цену товара"
    parser = LinkParser()
    parser.feed(text)
    assert {"/", "/about/", "/rules/", "/catalog/"}.issubset(set(parser.hrefs))
    assert any(h.endswith("css/style.css") for h in parser.stylesheets)


def test_unavailable_product_has_a_working_detail_page(client, product_factory):
    obj = product_factory(is_available=False)
    response = client.get(reverse("catalog:product_detail", args=(obj.pk,)))
    assert response.status_code == 200, "Отсутствующий в наличии товар тоже виден"
    assert response.context["product"].is_available is False


def test_availability_changes_visible_status(client, product_factory):
    obj = product_factory()
    url = reverse("catalog:product_detail", args=(obj.pk,))
    before = client.get(url).content
    obj.is_available = False
    obj.save()
    after = client.get(url).content
    assert before != after, "Выведите различающийся текст статуса наличия"


def test_next_request_sees_new_and_changed_data(client, product_factory):
    url = reverse("catalog:catalog_list")
    client.get(url)
    obj = product_factory(name="Новый товар после первого запроса")
    assert obj.name in client.get(url).content.decode()
    obj.name = "Переименованный товар"
    obj.description = "Изменённое описание из базы"
    obj.save()
    text = client.get(reverse("catalog:product_detail", args=(obj.pk,))).content.decode()
    assert obj.name in text and obj.description in text
    assert obj.name in client.get(url).content.decode()


def test_deleted_product_disappears_and_returns_404(client, product_factory):
    obj = product_factory(name="Товар для удаления")
    url = reverse("catalog:product_detail", args=(obj.pk,))
    assert client.get(url).status_code == 200
    name = obj.name
    obj.delete()
    assert client.get(url).status_code == 404
    assert name not in client.get(reverse("catalog:catalog_list")).content.decode()


def test_empty_catalog_has_a_readable_message(client, Product):
    Product.objects.all().delete()
    response = client.get(reverse("catalog:catalog_list"))
    assert response.status_code == 200
    assert list(response.context["products"]) == []
    # Проверяем сообщение в main, не фиксируя его формулировку.
    class EmptyMessageParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_main = False
            self.skip = 0
            self.parts = []

        def handle_starttag(self, tag, attrs):
            if tag == "main":
                self.in_main = True
            if tag in {"h1", "nav", "script", "style"}:
                self.skip += 1

        def handle_endtag(self, tag):
            if tag == "main":
                self.in_main = False
            if tag in {"h1", "nav", "script", "style"}:
                self.skip -= 1

        def handle_data(self, data):
            if self.in_main and not self.skip:
                self.parts.append(data)

    message = EmptyMessageParser()
    message.feed(response.content.decode())
    assert "".join(message.parts).strip(), "Добавьте сообщение о пустом каталоге"
    parser = LinkParser()
    parser.feed(response.content.decode())
    assert not any(h.startswith("/catalog/") and h != "/catalog/" for h in parser.hrefs)


@pytest.mark.parametrize("url", ["/catalog/0/", "/catalog/987654321/", "/catalog/abc/", "/catalog/-1/"])
def test_unknown_or_invalid_product_returns_404(client, url):
    assert client.get(url).status_code == 404
