from django.db import models


class Chemical(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cas_number = models.CharField(max_length=32, blank=True, db_index=True)
    formula = models.CharField(max_length=128, blank=True, db_index=True)
    storage_instructions = models.TextField(blank=True)
    synonyms = models.ManyToManyField("ChemicalSynonym", blank=True, related_name="chemicals")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ChemicalSynonym(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "chemical synonyms"

    def __str__(self):
        return self.name


class ManufacturerProduct(models.Model):
    chemical = models.ForeignKey(Chemical, on_delete=models.CASCADE, related_name="products")
    manufacturer = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255, blank=True)
    catalog_number = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["manufacturer", "product_name", "catalog_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["chemical", "manufacturer", "catalog_number"],
                name="unique_chemical_manufacturer_catalog",
            ),
        ]

    def __str__(self):
        label = self.product_name or self.chemical.name
        return f"{self.manufacturer} {label}".strip()


class SafetyDataSheet(models.Model):
    chemical = models.ForeignKey(Chemical, on_delete=models.CASCADE, related_name="safety_data_sheets")
    title = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=1000)
    revision_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-revision_date", "title"]

    def __str__(self):
        return self.title or f"SDS for {self.chemical.name}"


class StorageLocation(models.Model):
    name = models.CharField(max_length=255, unique=True)
    building = models.CharField(max_length=128, blank=True)
    room = models.CharField(max_length=128, blank=True)
    details = models.CharField(max_length=255, blank=True)
    chemicals = models.ManyToManyField(Chemical, through="ChemicalLocation", related_name="locations")

    class Meta:
        ordering = ["building", "room", "name"]

    def __str__(self):
        return self.name


class ChemicalLocation(models.Model):
    chemical = models.ForeignKey(Chemical, on_delete=models.CASCADE)
    location = models.ForeignKey(StorageLocation, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["chemical", "location"], name="unique_chemical_location"),
        ]

    def __str__(self):
        return f"{self.chemical} at {self.location}"
