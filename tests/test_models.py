from decimal import Decimal

import pytest
from django.db import models


def test_product_is_a_django_model(Product):
    assert issubclass(Product, models.Model)
    assert Product._meta.app_label == "catalog"


@pytest.mark.parametrize("name,field_type", [
    ("name", models.CharField),
    ("description", models.TextField),
    ("price", models.DecimalField),
    ("is_available", models.BooleanField),
])
def test_field_types(Product, name, field_type):
    assert isinstance(Product._meta.get_field(name), field_type), (
        f"Поле {name} должно иметь тип {field_type.__name__}"
    )


def test_name_length_and_required_fields(Product):
    assert Product._meta.get_field("name").max_length == 120
    for name in ("name", "description", "price"):
        field = Product._meta.get_field(name)
        assert not field.blank, f"Поле {name} должно быть обязательным"
        assert not field.null, f"Поле {name} не должно хранить NULL"


def test_price_precision(Product):
    field = Product._meta.get_field("price")
    assert (field.max_digits, field.decimal_places) == (10, 2), (
        "Для цены задайте max_digits=10 и decimal_places=2"
    )


def test_availability_defaults_to_true(Product):
    assert Product._meta.get_field("is_available").get_default() is True


@pytest.mark.django_db
def test_product_can_be_saved_and_read(Product):
    obj = Product.objects.create(
        name="Товар из базы", description="Полное описание", price="1999.90"
    )
    saved = Product.objects.get(pk=obj.pk)
    assert saved.pk is not None
    assert saved.name == "Товар из базы"
    assert saved.description == "Полное описание"
    assert saved.price == Decimal("1999.90")
    assert saved.is_available is True
    assert str(saved) == saved.name, "Метод __str__ должен возвращать name"


@pytest.mark.django_db
def test_product_can_be_changed_and_deleted(product_factory, Product):
    obj = product_factory()
    obj.price = Decimal("70.25")
    obj.is_available = False
    obj.save()
    obj.refresh_from_db()
    assert obj.price == Decimal("70.25")
    assert obj.is_available is False
    product_id = obj.pk
    obj.delete()
    assert not Product.objects.filter(pk=product_id).exists()
