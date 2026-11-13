from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("<int:pk>/", views.chemical_detail, name="chemical_detail"),
]
