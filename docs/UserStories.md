# Phase I user stories

## Access and platforms

### US-01 — Cross-platform access
As a laboratory user, I want to use the application on desktop, iPhone, and Android devices so that I can manage chemicals wherever I am working.
- The application works on all three platform categories.
- Camera scanning works on supported mobile devices.
- Core workflows are demonstrated with real containers and locations.

### US-02 — Role-based access
As an administrator, I want users assigned appropriate permissions so that students cannot alter protected inventory data.
- Student and administrative permissions are distinct.
- Students cannot edit records, change statuses, or manage users.
- Administrators can manage users and permissions.

## Search, identification, and SDS access
### US-03 — Search for chemicals
As a laboratory user, I want to search for a chemical using several identifiers so that I can find it without possessing the container.
- Search supports chemical name, alternate/common name, CAS number, and chemical formula.
- Partial searches, synonyms, and duplicate manufacturer products are handled appropriately.
- Results provide access to the chemical record, SDS, storage information, and location.

### US-04 — Scan a container
As a laboratory user, I want to scan a container QR code so that I can immediately open the correct container and chemical record.
- Every physical container has a unique institutional identifier.
- The QR code references the database record rather than embedding all chemical data.
- Scanning opens the correct record on each required platform.

### US-05 — Use manufacturer barcodes
As a laboratory user, I want to scan supported manufacturer barcodes so that I can identify products and simplify inventory entry.
- A manufacturer barcode may identify a product.
- The system does not treat it as a unique identifier for an individual container.
- 
### US-06 — Access an SDS
As a laboratory user, I want to open the appropriate SDS from a scanned or searched chemical record so that I can review its safety information quickly.
- Each applicable product is associated with the correct SDS.
- Manufacturer- or formulation-specific SDS associations are supported.
- An SDS can be opened after scanning or searching.
  
## Storage and location tracking
### US-07 — View storage requirements
As a laboratory user, I want to see a chemical’s Flinn classification and assigned storage location so that I know where it belongs.
- Information is available through both scanning and searching.
- The application displays the supplied classification without attempting to calculate it.
### US-08 — Locate a container
As a laboratory user, I want to see a container’s current location so that I can find it.
- Assigned storage location and current location are stored separately.
- Locations support buildings, rooms, cabinets, shelves, laboratories, hoods, benches, and designated work areas.
- 
### US-09 — Check out a chemical
As a laboratory user, I want to scan a chemical and its destination so that its movement to a working location is recorded with minimal effort.
- Workflow: scan chemical → scan destination → confirm.
- Current location is updated.
- The transaction records container, previous location, new location, user, date, and time.

### US-10 — Return a chemical
  As a laboratory user, I want to scan a chemical and its storage location so that the inventory records its return.
- Workflow: scan chemical → scan storage location → confirm.
- Current location is updated and a transaction is recorded.

### US-11 — Review movement history
As an administrator, I want to review a container’s transaction history so that I can investigate its movement.
- Authorized users can view chronological transaction history.
- Student users cannot edit the history.

## Inventory administration

### US-12 — Add products and containers
As an administrator, I want to add a product with one or more physical containers so that every bottle can be tracked independently.
- Chemical substance, commercial product, SDS, and physical container are distinct records.
- Multiple containers can share product and SDS data.
- Each container receives a unique inventory identifier.

### US-13 — Maintain inventory details
 As an administrator, I want to edit chemical, product, container, quantity, condition, and location information so that the inventory remains accurate.
- Required identity, product, container, storage, location, status, and history fields are supported.
- Inventory can be searched, sorted, and filtered.

### US-14 — Manage lifecycle status
As an administrator, I want to record statuses such as In Storage, In Use, Empty, Disposed, Missing, and Removed so that inactive materials are handled correctly.
- Status changes are recorded.
- Disposal can be documented.
- Historical information remains available when a record leaves the active inventory.

### US-15 — Manage SDS associations
As an administrator, I want to add or replace an SDS for a product so that users receive the appropriate document.
- SDS association accounts for manufacturer and formulation.
- Replacing an SDS does not incorrectly alter unrelated products.

### US-16 — Manage locations
As an administrator, I want to create and modify hierarchical storage and working locations so that containers can be assigned and tracked accurately.
- Administrators can create rooms, cabinets, shelves, hoods, benches, and other locations.
- Administrators can correct an inaccurate container location.
  
## Labels and physical auditing

### US-17 — Generate and print labels
As an administrator, I want to generate container and location QR labels so that physical items and locations can be scanned.
- Labels can be printed individually and in groups.
- Each label includes a scannable QR code and human-readable identifier.
- Printed labels scan successfully.

### US-18 — Reprint an existing label
As an administrator, I want to reprint a damaged or missing label so that the original record remains usable.
- The reprinted label retains the original identifier.
- Reprinting does not create a new inventory record.

### US-19 — Conduct a physical inventory audit
As an administrator, I want to scan containers during an audit so that I can verify their presence and locations.
- The system records which expected containers were scanned.
- Presence and location can be compared with inventory records.
- Missing or misplaced containers can be identified.

## Maintenance and deployment

### US-20 — Install and operate from documentation
As a future maintainer, I want complete installation, deployment, database, user, administrator, and technical documentation so that another class can run and extend the application.
- A person outside the original team can install and run the application.
- Source code and database documentation are delivered.
- The architecture separates chemical, product, SDS, container, location, and transaction data.

### US-21 — Preserve Phase II extensibility
As a future development team, I want an extensible data model so that safety guidance can be added without rebuilding Phase I.
- The architecture can later relate chemicals and products to hazards, handling guidance, incompatibilities, and disposal guidance.

# Phase II roadmap stories
 
### US-22: As a student, I want explanations of SDS sections so that I can interpret the document.
### US-23: As a student, I want explanations of GHS symbols, signal words, and hazard statements so that I understand their significance.
### US-24: As a student, I want plain-language definitions of technical safety terms so that I can interpret values such as flash point, exposure limits, and LD50.
### US-25: As a laboratory user, I want chemical- or hazard-specific handling guidance so that I can select suitable PPE, ventilation, and spill procedures.
### US-26: As a laboratory user, I want disposal guidance so that I can select appropriate waste streams, containers, labels, and temporary storage.

# Requirements that need clarification
  
- Whether faculty and laboratory staff are students, administrators, or separate roles.
- The authentication method and account source.
- Whether SDS files are hosted internally, linked externally, or both.
- Supported barcode formats, printers, label sizes, and browsers.
- The exact inventory-import format and data-cleanup responsibility.
- Audit behavior for missing, unexpected, or incorrectly located containers.
- Backup frequency, recovery targets, retention, and transaction-history immutability.
- Whether network connectivity is guaranteed inside laboratories.
- Required accessibility, privacy, security, and concurrent-editing behavior.
