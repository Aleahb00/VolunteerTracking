# Overview
The system is built using a relational database structure where all data is centered around disaster events. Each disaster serves as a parent entity that links volunteer and donation records, allowing data to be organized, tracked, and reported per disaster.

## 1. Core Entities
The system consists of three primary models:
* Disaster
* Volunteer
* Donations
Each model represents a key part of the disaster response process.

## 2. Relationships
* A Disaster can have many Volunteers
* A Disaster can have many Donations

This creates a one-to-many relationship:
* One disaster → many volunteer entries
* One disaster → many donation entries
All volunteer and donation records must be associated with a disaster.

## 3. Disaster Model
The Disaster model represents a specific disaster event being tracked.

### Key Fields:
* **name / number** → Identifies the disaster
* **type / category / size** → Classification details
* **location** → Area affected
* **start_date / end_date** → Duration of the event
* **declaration_date** → Official declaration date
* **completion_date** → When the disaster is considered complete

### Rates:
* **hourly_rate** → Standard value of volunteer time
* **skilled_hourly_rate** → Value for verified skilled labor

### Other Fields:
* **goal** → Target total (hours or value)
* **active** → Controls whether the disaster appears in public forms

## 4. Volunteer Model
The Volunteer model stores all volunteer submissions.

### Key Fields:
* name
* contact_method (email or phone)
* email / phone_number
* date_of_work
* total_hours
* location_volunteered
* work_desc

### Equipment Tracking:
* Predefined equipment options
* **other_equipment** field for custom input

### Skilled Worker Logic:
* **skilled_worker** → User-selected value (Yes / No / Unsure)
* **confirmed_skilled_worker** → Admin verification

### Flagging System:
* **flagged** (True/False)
* **flagged_reason** (JSON)
Used to mark entries that require review.

### Soft Deletion:
* Uses soft delete functionality
* Records are not permanently removed
* Allows recovery and audit tracking

## 5. Donations Model
The Donations model stores all donation submissions.

### Key Fields:
* name
* contact_method
* email / phone_number
* date_of_donation
* location_donated
* work_desc

### Donation Types:
* Material
* Equipment
* Money
* Other

### Type-Specific Fields:
* material_type
* equipment_type
* money_donated
* other_donation_type

### Limits:
* Monetary donations capped at $999,999.99

### Flagging & Soft Delete:
* Same system as Volunteer model
* Ensures consistency and auditability

## 6. Key System Logic
### Hour Validation:
* Maximum of 18 hours per entry

### Value Calculation:
* Standard hours use **hourly_rate**
* Verified skilled hours use **skilled_hourly_rate**

### Disaster Dependency:
* All records must be linked to a disaster
* Only active disasters are available for submissions

## 7. Data Integrity & Design Decisions
### Centralized Disaster Model
All data is tied to a disaster, allowing:
* Organized reporting
* Disaster-specific analytics
* Scalable multi-event tracking

### Soft Deletion for Compliance
Data is never permanently removed to:
* Support audits
* Allow recovery of records
* Maintain historical accuracy

### Flagging System
Provides a way to:
* Identify suspicious or incorrect data
* Allow admin review before final reporting

### Flexible Data Structure
Use of optional fields allows:
* Different types of donations
* Variable equipment tracking
* Adaptability across different disaster scenarios