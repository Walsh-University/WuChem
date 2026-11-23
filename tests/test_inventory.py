from datetime import date

import pytest
from django.core.exceptions import ValidationError
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


def test_search_and_detail_show_product_specific_sds(signed_in_client, chemical_record):
    product = ManufacturerProduct.objects.create(
        chemical=chemical_record,
        manufacturer="Acme Chemicals",
        product_name="Anhydrous Acetone",
        catalog_number="ACME-42",
    )
    SafetyDataSheet.objects.create(
        chemical=chemical_record,
        product=product,
        title="Acme Anhydrous Acetone SDS",
        url="https://example.com/acme-42-sds.pdf",
    )

    search_response = signed_in_client.get(reverse("chem_core:search"), {"q": "ACME-42"})
    detail_response = signed_in_client.get(reverse("inventory:chemical_detail", args=[chemical_record.pk]))

    assert "https://example.com/acme-42-sds.pdf" in search_response.content.decode()
    assert "Acme Chemicals Anhydrous Acetone" in search_response.content.decode()
    assert "https://example.com/acme-42-sds.pdf" in detail_response.content.decode()
    assert "Acme Chemicals Anhydrous Acetone: Acme Anhydrous Acetone SDS" in detail_response.content.decode()


def test_search_and_detail_distinguish_general_and_multiple_product_sds(signed_in_client, chemical_record):
    acme_product = ManufacturerProduct.objects.create(
        chemical=chemical_record,
        manufacturer="Acme Chemicals",
        product_name="Anhydrous Acetone",
        catalog_number="ACME-42",
    )
    example_product = ManufacturerProduct.objects.create(
        chemical=chemical_record,
        manufacturer="Example Labs",
        product_name="Acetone Solution",
        catalog_number="EX-17",
    )
    SafetyDataSheet.objects.create(
        chemical=chemical_record,
        title="General Acetone SDS",
        url="https://example.com/acetone-general.pdf",
    )
    SafetyDataSheet.objects.create(
        chemical=chemical_record,
        product=acme_product,
        title="Acme SDS",
        url="https://example.com/acme.pdf",
    )
    SafetyDataSheet.objects.create(
        chemical=chemical_record,
        product=example_product,
        title="Example Labs SDS",
        url="https://example.com/example-labs.pdf",
    )

    search_response = signed_in_client.get(reverse("chem_core:search"), {"q": "acetone"})
    detail_response = signed_in_client.get(reverse("inventory:chemical_detail", args=[chemical_record.pk]))

    for response in (search_response, detail_response):
        content = response.content.decode()
        assert "https://example.com/acetone-general.pdf" in content
        assert "https://example.com/acme.pdf" in content
        assert "https://example.com/example-labs.pdf" in content
        assert "Acme Chemicals Anhydrous Acetone: Acme SDS" in content
        assert "Example Labs Acetone Solution: Example Labs SDS" in content


def test_chemical_detail_shows_empty_sds_state(signed_in_client, chemical_record):
    response = signed_in_client.get(reverse("inventory:chemical_detail", args=[chemical_record.pk]))

    assert response.status_code == 200
    assert "No safety data sheet is linked yet." in response.content.decode()


def test_sds_product_must_belong_to_its_chemical(chemical_record):
    other_chemical = Chemical.objects.create(name="Ethanol")
    product = ManufacturerProduct.objects.create(
        chemical=other_chemical,
        manufacturer="Example Labs",
        catalog_number="ETH-1",
    )
    with pytest.raises(ValidationError, match="associated with this chemical"):
        SafetyDataSheet.objects.create(
            chemical=chemical_record,
            product=product,
            title="Mismatched SDS",
            url="https://example.com/mismatched-sds.pdf",
        )
