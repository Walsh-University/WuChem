-- Test-only inventory seed data for WuChem.
--
-- Prerequisite: apply Django migrations before running this script.
-- Example:
--   psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f scripts/seed_inventory.sql
--
-- The script is transactional and idempotent: rerunning it updates the seeded
-- records where the schema provides a natural key and avoids duplicate links.

BEGIN;

INSERT INTO inventory_chemical (
    name,
    cas_number,
    formula,
    storage_instructions
)
VALUES
    (
        'Acetone',
        '67-64-1',
        'C3H6O',
        'Store in the designated flammable-liquids storage area.'
    ),
    (
        'Ethanol',
        '64-17-5',
        'C2H6O',
        'Store in the designated flammable-liquids storage area.'
    ),
    (
        'Hydrochloric acid',
        '7647-01-0',
        'HCl',
        'Store in the designated corrosives storage area.'
    ),
    (
        'Sodium hydroxide',
        '1310-73-2',
        'NaOH',
        'Store in the designated corrosives storage area.'
    ),
    (
        'Sodium chloride',
        '7647-14-5',
        'NaCl',
        'Store in a cool, dry general-chemicals storage area.'
    ),
    (
        'Copper(II) sulfate pentahydrate',
        '7758-99-8',
        'CuSO4·5H2O',
        'Store in a cool, dry general-chemicals storage area.'
    )
ON CONFLICT (name) DO UPDATE
SET
    cas_number = EXCLUDED.cas_number,
    formula = EXCLUDED.formula,
    storage_instructions = EXCLUDED.storage_instructions;

INSERT INTO inventory_chemicalsynonym (name)
VALUES
    ('2-propanone'),
    ('Ethyl alcohol'),
    ('Muriatic acid'),
    ('Caustic soda'),
    ('Table salt'),
    ('Blue vitriol')
ON CONFLICT (name) DO NOTHING;

INSERT INTO inventory_chemical_synonyms (chemical_id, chemicalsynonym_id)
SELECT chemical.id, synonym.id
FROM (
    VALUES
        ('Acetone', '2-propanone'),
        ('Ethanol', 'Ethyl alcohol'),
        ('Hydrochloric acid', 'Muriatic acid'),
        ('Sodium hydroxide', 'Caustic soda'),
        ('Sodium chloride', 'Table salt'),
        ('Copper(II) sulfate pentahydrate', 'Blue vitriol')
) AS seed(chemical_name, synonym_name)
JOIN inventory_chemical AS chemical
    ON chemical.name = seed.chemical_name
JOIN inventory_chemicalsynonym AS synonym
    ON synonym.name = seed.synonym_name
ON CONFLICT (chemical_id, chemicalsynonym_id) DO NOTHING;

INSERT INTO inventory_manufacturerproduct (
    chemical_id,
    manufacturer,
    product_name,
    catalog_number
)
SELECT
    chemical.id,
    seed.manufacturer,
    seed.product_name,
    seed.catalog_number
FROM (
    VALUES
        ('Acetone', 'TestChem', 'Acetone, ACS grade', 'TC-A100'),
        ('Acetone', 'Example Scientific', 'Acetone, HPLC grade', 'ES-AC-2500'),
        ('Ethanol', 'TestChem', 'Ethanol, 200 proof', 'TC-E200'),
        ('Hydrochloric acid', 'Example Scientific', 'Hydrochloric acid, 37%', 'ES-HCL-37'),
        ('Sodium hydroxide', 'TestChem', 'Sodium hydroxide pellets', 'TC-SH500'),
        ('Sodium chloride', 'Example Scientific', 'Sodium chloride, ACS grade', 'ES-NACL-1K'),
        ('Copper(II) sulfate pentahydrate', 'TestChem', 'Copper sulfate pentahydrate', 'TC-CS250')
) AS seed(chemical_name, manufacturer, product_name, catalog_number)
JOIN inventory_chemical AS chemical
    ON chemical.name = seed.chemical_name
ON CONFLICT (chemical_id, manufacturer, catalog_number) DO UPDATE
SET product_name = EXCLUDED.product_name;

INSERT INTO inventory_safetydatasheet (
    chemical_id,
    title,
    url,
    revision_date
)
SELECT
    chemical.id,
    seed.title,
    seed.url,
    seed.revision_date
FROM (
    VALUES
        ('Acetone', 'Acetone test SDS', 'https://example.invalid/sds/acetone.pdf', DATE '2026-01-15'),
        ('Ethanol', 'Ethanol test SDS', 'https://example.invalid/sds/ethanol.pdf', DATE '2026-02-01'),
        ('Hydrochloric acid', 'Hydrochloric acid test SDS', 'https://example.invalid/sds/hydrochloric-acid.pdf', DATE '2025-12-10'),
        ('Sodium hydroxide', 'Sodium hydroxide test SDS', 'https://example.invalid/sds/sodium-hydroxide.pdf', DATE '2026-03-05'),
        ('Sodium chloride', 'Sodium chloride test SDS', 'https://example.invalid/sds/sodium-chloride.pdf', DATE '2025-11-20'),
        ('Copper(II) sulfate pentahydrate', 'Copper sulfate test SDS', 'https://example.invalid/sds/copper-sulfate.pdf', DATE '2026-04-12')
) AS seed(chemical_name, title, url, revision_date)
JOIN inventory_chemical AS chemical
    ON chemical.name = seed.chemical_name
WHERE NOT EXISTS (
    SELECT 1
    FROM inventory_safetydatasheet AS existing
    WHERE existing.chemical_id = chemical.id
      AND existing.url = seed.url
);

INSERT INTO inventory_storagelocation (name, building, room, details)
VALUES
    ('Flammables cabinet A', 'Science Hall', '101', 'Lower shelf'),
    ('Corrosives cabinet B', 'Science Hall', '101', 'Acids section'),
    ('Corrosives cabinet C', 'Science Hall', '101', 'Bases section'),
    ('General chemicals shelf 2', 'Science Hall', '103', 'Dry storage')
ON CONFLICT (name) DO UPDATE
SET
    building = EXCLUDED.building,
    room = EXCLUDED.room,
    details = EXCLUDED.details;

INSERT INTO inventory_chemicallocation (chemical_id, location_id)
SELECT chemical.id, location.id
FROM (
    VALUES
        ('Acetone', 'Flammables cabinet A'),
        ('Ethanol', 'Flammables cabinet A'),
        ('Hydrochloric acid', 'Corrosives cabinet B'),
        ('Sodium hydroxide', 'Corrosives cabinet C'),
        ('Sodium chloride', 'General chemicals shelf 2'),
        ('Copper(II) sulfate pentahydrate', 'General chemicals shelf 2')
) AS seed(chemical_name, location_name)
JOIN inventory_chemical AS chemical
    ON chemical.name = seed.chemical_name
JOIN inventory_storagelocation AS location
    ON location.name = seed.location_name
ON CONFLICT (chemical_id, location_id) DO NOTHING;

COMMIT;
