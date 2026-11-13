from django.urls import path

from chem_core import views
from inventory import views as inventory_views

app_name = "chem_core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("search/", inventory_views.search, name="search"),
    path("api/status", views.status_public, name="status_public"),
    path("api/status/internal", views.status_internal, name="status_internal"),
]
