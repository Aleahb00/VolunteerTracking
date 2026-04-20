# Overview
The system allows administrators to manage disaster events, track volunteer activity, monitor donations, and generate reports for analysis and compliance.
The dashboard is divided into two main views:
* General Dashboard (global overview)
* Disaster Dashboard (project-specific view)

## 1. Admin Dashboard Structure
### General Dashboard (Global View):
This is the main page administrators see after logging in.
From the General Dashboard, admins can:
* View all disasters (at first by default the admin sees all active but by clicking o the switch it can show all projects: active and inactive)
* Identify flagged volunteers and donations across all disasters
* Create a new disaster
* Navigate to a specific disaster dashboard
* Manage their account
* View Trash 

#### Key Features:
* Disaster List → Displays all disasters
* Flagged Entries Section → Shows entries that require attention
* Navigation Controls → Access individual disaster dashboards

### Disaster Dashboard (Project-Specific View):
When an admin selects “View Dashboard” on a disaster, they are taken to a detailed dashboard for that specific event.
Inside a Disaster Dashboard:
Admins can view and manage:
* Volunteer submissions
* Donation records
* Flagged donation and volunteers
* Total hours contributed
* Total monetary value
* How far away they are from their goal 
* Edit the disaster information 
* View detailed volunteer and donation forms 

## 2. Managing Disasters
### Creating a Disaster
1. Navigate to the General Dashboard
2. Click Create Disaster
3. Fill in the following:
    * Name
    * Number
    * Type / Category / Size
    * Location
    * Start Date / End Date
    * Declaration Date
    * Completion Date
    * Goal
    * Hourly Rate
    * Skilled Hourly Rate

### Accessing a Disaster Dashboard
1. Go to the General Dashboard
2. Locate a disaster
3. Click “View Dashboard”

### Closing a Disaster
1. Navigate to General dashboard 
2. Click on the disaster you want to close 
3. Click on setting and click on “Close Disaster”

This will:
* Reject any form that want to be added to that project 
* It will become read only 
* **ONCE A PROJECT IS CLOSE THIS ACTION CAN NOT BE UNDONE.**

## 3. Volunteer Management
### Viewing Volunteer Submissions
* Access through the Disaster Dashboard
* Filter by disaster
* View details such as:
    * Name
    * Location
    * Date
    * Contact

### Volunteer Hour Limits
* Volunteers can log a maximum of 16 hours per day
* This prevents unrealistic or inaccurate reporting

### Skilled Worker Verification
Each submission includes:
* Skilled Worker (Yes / No / Unsure) → selected by user
* Confirmed Skilled Worker (True / False) → set by admin

#### Important:
* Not confirmed → uses standard hourly rate
* Confirmed → uses skilled hourly rate

### Equipment Tracking
* Volunteers select from predefined equipment options
* If “Other” is selected:
    * Admins should review the additional input field

### Flagged Entries 
Flagged forms appear in:
* General Dashboard → all flagged forms
* Disaster Dashboard → disaster-specific forms

#### Common reasons:
* Invalid location
* Inconsistent skilled worker selection
* Too many submissions being submitted at once 

### Handling Flagged Forms
1. Identify flagged records
2. Open the disaster dashboard
3. Review entry details
4. View flagged_reason
5. Verify information or contact the user
6. Resolve and update the entry
7. Remove flag if appropriate

### Deleting Volunteers (Soft Delete)
Deleting does NOT permanently remove data
Records are hidden but retained for:
* Audits
* Data recovery

## 4. Donation Management
### Viewing Donations
* Access through the Disaster Dashboard
* Filter by disaster
* Donation Type
    * Material
    * Equipment
    * Money (The site is not taking any type of payment it is just logging the amount donated)
    * Other

### Monetary Donations
* Maximum allowed: $999,999.99
* Enforced by system validation

### Donation Hours
* Some donations include hours
* These contribute to total impact calculations

### Flagged Donations
* Follow the same process as volunteer flagged entries
* Review, verify, and resolve

### Deleting Donation Forms (Soft Delete)
Deleting does NOT permanently remove data
Records are hidden but retained for:
* Audits
* Data recovery

## 5. Data Export & Reporting
### Exporting Data
1. Navigate to reporting/export section
2. Select a disaster
3. Choose export format:
    * CSV
    * Excel

### Printing Data 
1. Access through the Disaster Dashboard
2. Click on “View Disaster Submission”
3. View all details for volunteers and donation forms 
4. Have the option to print all, print selected, or just print one

## 6. User Management
From the General Dashboard, admins can:
* Manage their account
* Update login credentials
* Change password
* Logout

## 7. Data Rules & System Limitations
* Maximum 16 hours per day per volunteer
* Donation cap of $999,999.99
* Required fields must be completed
* Some fields appear conditionally (e.g., “Other” fields)

## 8. Data Privacy & Responsibility
The system collects:
* Email addresses
* Phone numbers

This data:
* Is only accessible to administrators
* Should be handled responsibly
* Data is not permanently deleted but it can be by clicking the delete permanently button in the trash panel.