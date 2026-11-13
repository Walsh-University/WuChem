from datetime import date

import pytest
from django.urls import reverse

from inventory.models import (
    Chemical,
    ChemicalSynonym,
    ManufacturerProduct,
    SafetyDataSheet,
    StorageLocation,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def signed_in_client(client, django_user_model):
    user = django_user_model.objects.create_user(username="lab-user", password="test-password")
    client.force_login(user)
    return client


@pytest.fixture
def chemical_record():
    chemical = Chemical.objects.create(
        name="Acetone",
        cas_number="67-64-1",
        formula="C3H6O",
        storage_instructions="Store in a flammable liquids cabinet.",
    )
    synonym = ChemicalSynonym.objects.create(name="2-propanone")
    chemical.synonyms.add(synonym)
    return chemical


def test_chemical_search_requires_login(client):
    response = client.get(reverse("chem_core:search"), {"q": "acetone"})

    assert response.status_code == 302


@pytest.mark.parametrize(
    "query",
    ["acet", "2-prop", "67-64", "C3H", "ACME-42"],
)
def test_search_matches_partial_identifiers_and_product_details(signed_in_client, chemical_record, query):
    ManufacturerProduct.objects.create(
        chemical=chemical_record,
        manufacturer="Acme Chemicals",
        product_name="Acetone solvent",
        catalog_number="ACME-42",
    )

    response = signed_in_client.get(reverse("chem_core:search"), {"q": query})

    assert response.status_code == 200
    assert list(response.context["chemicals"]) == [chemical_record]


def test_search_returns_a_chemical_once_when_multiple_products_match(signed_in_client, chemical_record):
    ManufacturerProduct.objects.create(
        chemical=chemical_record,
        manufacturer="Acme Chemicals",
        product_name="Acetone",
        catalog_number="ACME-1",
    )
    ManufacturerProduct.objects.create(
        chemical=chemical_record,
        manufacturer="Example Labs",
        product_name="Acetone reagent",
        catalog_number="EX-2",
    )

    response = signed_in_client.get(reverse("chem_core:search"), {"q": "acet"})

    assert response.status_code == 200
    assert list(response.context["chemicals"]) == [chemical_record]
    assert response.content.decode().count('class="card"') == 1


def test_search_results_link_to_sds_and_show_storage_and_location(signed_in_client, chemical_record):
    SafetyDataSheet.objects.create(
        chemical=chemical_record,
        title="Acetone SDS",
        url="https://example.com/acetone-sds.pdf",
        revision_date=date(2026, 1, 15),
    )
    location = StorageLocation.objects.create(
        name="Flammables cabinet 2",
        building="Science Hall",
        room="101",
        details="Lower shelf",
    )
    location.chemicals.add(chemical_record)

    response = signed_in_client.get(reverse("chem_core:search"), {"q": "acetone"})
    detail_response = signed_in_client.get(reverse("inventory:chemical_detail", args=[chemical_record.pk]))

    assert response.status_code == 200
    assert reverse("inventory:chemical_detail", args=[chemical_record.pk]) in response.content.decode()
    assert "https://example.com/acetone-sds.pdf" in response.content.decode()
    assert "Store in a flammable liquids cabinet." in response.content.decode()
    assert "Flammables cabinet 2" in response.content.decode()
    assert "Lower shelf" in response.content.decode()

    assert detail_response.status_code == 200
    assert "Acetone SDS" in detail_response.content.decode()
    assert "Science Hall" in detail_response.content.decode()
