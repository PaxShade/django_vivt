from io import StringIO

import pytest
from django.contrib import admin
from django.core.management import call_command
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.urls import reverse


@pytest.mark.django_db
def test_catalog_has_a_product_migration(Product):
    loader = MigrationLoader(connection)
    state = loader.project_state()
    assert ("catalog", "product") in state.models, (
        "Создайте миграцию Product командой makemigrations catalog"
    )
    assert any(app == "catalog" for app, name in loader.disk_migrations), (
        "В catalog/migrations должен быть файл миграции"
    )


@pytest.mark.django_db
def test_catalog_migrations_match_models(Product):
    call_command("makemigrations", "catalog", check=True, dry_run=True,
                 stdout=StringIO(), stderr=StringIO())


def test_django_system_checks():
    call_command("check", stdout=StringIO(), stderr=StringIO())


def test_product_is_registered_in_admin(Product):
    assert admin.site.is_registered(Product), (
        "Зарегистрируйте Product в catalog/admin.py"
    )


@pytest.mark.django_db
def test_admin_requires_login(client):
    response = client.get("/admin/")
    assert response.status_code == 302
    assert reverse("admin:login") in response.url


@pytest.mark.django_db
def test_superuser_can_open_product_list(admin_client, Product, product_factory):
    product = product_factory(name="Товар в административной панели")
    url = reverse("admin:catalog_product_changelist")
    response = admin_client.get(url)
    assert response.status_code == 200
    assert product.name in response.content.decode(response.charset)
