from pathlib import Path

import pytest
from django.apps import apps


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def Product():
    __tracebackhide__ = True
    try:
        return apps.get_model("catalog", "Product")
    except LookupError:
        pytest.fail("Создайте модель Product в catalog/models.py", pytrace=False)


@pytest.fixture
def product_factory(db, Product):
    def create(**overrides):
        values = {
            "name": "Проверочный товар",
            "description": "Описание товара из тестовой базы",
            "price": "1234.50",
            "is_available": True,
        }
        values.update(overrides)
        return Product.objects.create(**values)
    return create
