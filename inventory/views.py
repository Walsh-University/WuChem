from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Chemical


def _chemical_search(query):
    return (
        Chemical.objects.filter(
            Q(name__icontains=query)
            | Q(cas_number__icontains=query)
            | Q(formula__icontains=query)
            | Q(synonyms__name__icontains=query)
            | Q(products__product_name__icontains=query)
            | Q(products__manufacturer__icontains=query)
            | Q(products__catalog_number__icontains=query)
        )
        .distinct()
        .prefetch_related("synonyms", "products", "safety_data_sheets", "locations")
    )


@login_required
def search(request):
    query = (request.GET.get("q") or "").strip()
    chemicals = _chemical_search(query) if query else Chemical.objects.none()
    return render(request, "inventory/search.html", {"q": query, "chemicals": chemicals})


@login_required
def chemical_detail(request, pk):
    chemical = get_object_or_404(
        Chemical.objects.prefetch_related("synonyms", "products", "safety_data_sheets", "locations"),
        pk=pk,
    )
    return render(request, "inventory/chemical_detail.html", {"chemical": chemical})
