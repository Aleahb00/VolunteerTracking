## Project Name
Volunteer Tracking 

## Client
ERassist

## Creators
- Aleah Bean
- Daniela Padilla
- Lemuel Tzib 

## Project Overview
Volunteer Tracking is a web-based application developed as a capstone project at Base Camp Coding Academy. It is designed specifically for ERassist to support disaster response operations across multiple locations.
The system provides a platform for tracking volunteer hours and donations during disaster relief efforts. It improves efficiency, organization, and reporting by allowing data to be collected and managed in one place.
This system is intended to be reusable for different disasters and locations, allowing ERassist to deploy it as needed for future events.


## System Description
The system includes both a public-facing interface and an administrative dashboard.

- **Public users** can submit volunteer hours and donation information through online forms, view through the website for FAQ’s, and also view the great impact the platform has done

- **Administrator (ERassist staff)** can manage disasters, monitor activity, review flagged submissions, and analyze data through the dashboard.

The platform is structured around two main dashboard views:

- **General Dashboard**
Provides an overview of all disasters, including flagged volunteer and donation entries across projects.

- **Disaster Dashboard**
Displays detailed, disaster-specific data such as volunteer contributions, donations, total impact, and progress toward goals.

All submitted data is stored in a centralized database and can be used for reporting, including compliance and audit purposes.

## Technologies Used
- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite 

### Libraries/Tools:
- **django-phonenumber-field / phonenumbers**
- Used to validate and properly format phone number inputs
- **django-widget-tweaks**
- Allows customization of form rendering in templates
- **RapidFuzz**
- Used for fuzzy matching (e.g., detecting similar or inconsistent inputs)
- **django-honeypot**
- Helps prevent spam form submissions using hidden fields
- **django-ratelimit**
- Protects forms and endpoints from abuse by limiting request frequency
- **django-safedelete**
- Enables soft deletion so records are not permanently removed (important for audits)
- **django-filter**
- Provides filtering capabilities for dashboard data (e.g., by disaster)
- **whitenoise**
- Handles serving static files in production environments

## User Roles (Brief)
### Public User

- Submit volunteer hours
- Submit donation information
- Provide contact details for follow-up

### Administrator (ERassist Staff)
- Create and manage disaster events
- View and manage volunteer and donation data
- Monitor and resolve flagged forms
- Access dashboards and analytics
- Export data for reporting (e.g., FEMA or internal use)