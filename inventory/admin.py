from django.contrib import admin

from .models import Chemical, ChemicalLocation, ChemicalSynonym, ManufacturerProduct, SafetyDataSheet, StorageLocation


class ManufacturerProductInline(admin.TabularInline):
    model = ManufacturerProduct
    extra = 0


class SafetyDataSheetInline(admin.TabularInline):
    model = SafetyDataSheet
    extra = 0


class ChemicalLocationInline(admin.TabularInline):
    model = ChemicalLocation
    extra = 0


@admin.register(Chemical)
class ChemicalAdmin(admin.ModelAdmin):
    list_display = ("name", "cas_number", "formula")
    search_fields = ("name", "cas_number", "formula", "synonyms__name", "products__product_name")
    inlines = (ManufacturerProductInline, SafetyDataSheetInline, ChemicalLocationInline)
    filter_horizontal = ("synonyms",)


@admin.register(ChemicalSynonym)
class ChemicalSynonymAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "building", "room")
    search_fields = ("name", "building", "room", "details")
