from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "relative_path",
    (
        "templates/base.html",
        "pages/templates/pages/index.html",
        "pages/templates/pages/about.html",
        "pages/templates/pages/rules.html",
        "catalog/templates/catalog/catalog_list.html",
        "catalog/templates/catalog/product_detail.html",
        "static/css/style.css",
    ),
)
def test_required_template_and_static_file_exists(relative_path):
    path = PROJECT_ROOT / relative_path
    assert path.is_file(), f"Не найден обязательный файл: {relative_path}"


@pytest.mark.parametrize(
    "relative_path",
    (
        "pages/templates/pages/index.html",
        "pages/templates/pages/about.html",
        "pages/templates/pages/rules.html",
        "catalog/templates/catalog/catalog_list.html",
        "catalog/templates/catalog/product_detail.html",
    ),
)
def test_page_template_extends_base(relative_path):
    source = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
    compact = " ".join(source.split())
    assert "{% extends" in compact and "base.html" in compact, (
        f"Шаблон {relative_path} должен наследоваться от base.html"
    )


def test_catalog_list_uses_template_loop():
    path = PROJECT_ROOT / "catalog/templates/catalog/catalog_list.html"
    source = " ".join(path.read_text(encoding="utf-8").split())
    assert "{% for" in source and "{% endfor %}" in source, (
        "Список товаров нужно сформировать циклом шаблона"
    )
    assert "{% empty %}" in source or "{% if" in source, (
        "Обработайте в шаблоне пустой список или условие отображения товара"
    )
