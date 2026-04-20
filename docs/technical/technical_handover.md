# Overview
This section provides technical details required for a developer to set up, run, and maintain the ERassist Volunteer Tracking. It includes environment setup, project structure, dependencies, and deployment considerations.

## 1. Environment Setup
### Requirements
* Python 3.x
* pip (Python package manager)
* Virtual environment tool (recommended)

### Installation Steps
1. Clone the repository
2. Navigate to the project directory
3. Create a virtual environment:
   `python3 -m venv venv`
4. Activate the virtual environment:
   * **macOS/Linux:** `source venv/bin/activate`
   * **Windows:** `venv\Scripts\activate`
5. Install dependencies:
   `pip install -r app/requirements.txt`

### Running the Application
`python manage.py migrate`  
`python manage.py runserver`

Access the application at:  
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 2. Dependencies
The project uses the following key packages:
* django-phonenumber-field
* phonenumbers
* django-widget-tweaks
* RapidFuzz
* django-honeypot
* django-ratelimit
* django-safedelete
* django-filter
* whitenoise

These are listed in `requirements.txt`.

## 3. Project Structure
The project is organized into the following main components:
* **app/**: Contains core application logic including: models, views, forms, templates
* **config/**: Contains project-level configuration: settings, URL routing, ASGI/WSGI setup
* **templates/**: HTML templates for: Public forms, General Dashboard, Disaster Dashboard
* **static/**: CSS, JavaScript, and other static assets

## 4. Database Setup
* Default database: SQLite
* Migrations are used to manage schema changes
* **Commands:**
  * `python manage.py makemigrations`
  * `python manage.py migrate`

## 5. Key System Features (Technical)
### Soft Delete
* Implemented using **django-safedelete**
* Records are marked as deleted but not removed from the database

### Rate Limiting & Security
* **django-ratelimit** prevents excessive requests
* **django-honeypot** helps prevent spam submissions

### Data Validation
* Phone number validation using **django-phonenumber-field**
* Field constraints (e.g., max hours, donation limits) enforced at model level

### Filtering & Querying
* **django-filter** is used for filtering dashboard data

## 6. Deployment Considerations
### Static Files
* Managed using **whitenoise** for production

### Environment Configuration
* Ensure **DEBUG** is set to `False` in production
* Configure allowed hosts
* Secure secret keys

### Database
* SQLite is suitable for development
* For production, consider upgrading to: **PostgreSQL** or another scalable database

## 7. Maintenance & Updates
### Regular Tasks
* Monitor logs for errors
* Backup database regularly
* Update dependencies as needed

### Adding Features
1. Follow Django app structure
2. Update models → run migrations
3. Update forms and views accordingly

## 8. Future Improvements
Potential enhancements include:
* not sure about these maybe for analytics or something like that 