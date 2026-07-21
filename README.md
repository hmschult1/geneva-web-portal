# Geneva App Portal

A secure, staff-facing Flask application for reviewing and managing Geneva College alumni submissions.

The portal connects to separate MySQL databases for alumni records and staff authentication. Authorized staff can sign in, review submitted alumni updates and class notes, edit records, and manage their account password.

## Features

* Database-backed staff authentication
* Secure password hashing and verification
* Protected staff-only routes with Flask-Login
* Thirty-minute inactivity timeout
* Alumni update review and editing
* Class note review and editing
* Account password management
* Separate SQLAlchemy database binds for:

  * alumni submission data
  * staff authentication data
* CSRF-protected forms
* MySQL SSL connection support
* Azure App Service deployment through GitHub Actions
* Model-mapping and staff-user tests

## Technology Stack

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Login
* Flask-WTF
* WTForms
* PyMySQL
* python-dotenv
* MySQL
* GitHub Actions
* Microsoft Azure App Service

## Project Structure

```text
geneva-app-portal/
├── .github/
│   └── workflows/
│       └── main_geneva-app-portal.yml
├── app/
│   ├── app_portal/
│   │   ├── templates/
│   │   │   └── app_portal/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── auth/
│   │   ├── templates/
│   │   │   └── auth/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   └── routes.py
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── commands.py
│   ├── extensions.py
│   └── models.py
├── tests/
│   ├── test_model_mapping.py
│   └── test_staff_user_model.py
├── .gitignore
├── config.py
├── requirements.txt
├── run.py
└── README.md
```

## Application Architecture

The project uses Flask’s application-factory pattern.

The application is created by:

```python
from app import create_app

app = create_app()
```

The `create_app()` function:

1. Creates the Flask application.
2. Loads configuration from `config.py`.
3. Initializes SQLAlchemy, CSRF protection, and Flask-Login.
4. Imports the application models.
5. Registers the authentication and portal blueprints.
6. Registers custom Flask CLI commands.

## Database Configuration

The application uses two SQLAlchemy binds.

| Bind     | Purpose                                                                                                                         |
| -------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `alumni` | Stores alumni records, submissions, class notes, education updates, employment updates, family updates, and related information |
| `auth`   | Stores staff user accounts and hashed passwords                                                                                 |

Both databases currently use the same MySQL host and database credentials, but each bind points to a different database name.

## Environment Variables

Create a `.env` file in the project root.

```env
SECRET_KEY=replace-with-a-long-random-secret

DB_HOST=your-mysql-server.mysql.database.azure.com
DB_USER=your-database-username
DB_PASSWORD=your-database-password

ALUMNI_DB_NAME=your-alumni-database
AUTH_DB_NAME=your-auth-database
```

### Variable Reference

| Variable         |    Required | Description                                   |
| ---------------- | ----------: | --------------------------------------------- |
| `SECRET_KEY`     | Recommended | Used to secure sessions and CSRF tokens       |
| `DB_HOST`        |         Yes | MySQL server hostname                         |
| `DB_USER`        |         Yes | MySQL username                                |
| `DB_PASSWORD`    |         Yes | MySQL password                                |
| `ALUMNI_DB_NAME` |         Yes | Database containing alumni submission records |
| `AUTH_DB_NAME`   |         Yes | Database containing staff user accounts       |

The application will not start if any required database variable is missing.

## Local Development Setup

### 1. Clone the repository

```powershell
git clone https://github.com/hmschult1/geneva-app-portal.git
cd geneva-app-portal
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
```

Activate it in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

For Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

For Git Bash:

```bash
source .venv/Scripts/activate
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the environment

Create a `.env` file in the project root and add the required variables:

```env
SECRET_KEY=development-secret-key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-password
ALUMNI_DB_NAME=alumni_schema
AUTH_DB_NAME=auth_schema
```

Do not commit the `.env` file.

### 5. Confirm the databases exist

The databases named by `ALUMNI_DB_NAME` and `AUTH_DB_NAME` must already exist and be accessible to the configured MySQL user.

For example:

```sql
CREATE DATABASE alumni_schema;
CREATE DATABASE auth_schema;
```

The MySQL user must have the required permissions for both databases.

### 6. Run the application

```powershell
python run.py
```

The development server will normally be available at:

```text
http://127.0.0.1:5000
```

Unauthenticated users will be redirected to the login page.

## Staff User Management

Staff accounts are stored in the authentication database rather than being defined in environment variables.

Passwords must be stored as password hashes. They should never be saved as plaintext.

### Create a staff user

The application registers a custom Flask CLI command named `create-user`.

Run:

```powershell
python -m flask --app run.py create-user
```

The command will prompt for:

* username
* email address
* password
* password confirmation

You may also provide values as command options:

```powershell
python -m flask --app run.py create-user `
    --username "staff-user" `
    --email "staff@example.com"
```

The password prompt remains hidden and requires confirmation.

### Login

Open the login page and enter the username and password associated with a staff account.

The application:

* looks up the user by username
* verifies the submitted password against the stored hash
* starts a Flask-Login session
* redirects the user to the originally requested safe URL or the portal landing page

### Logout

Users can explicitly end their session through the logout route.

### Password Changes

Authenticated users can change their password from the account page.

The password-change workflow:

1. Verifies the current password.
2. Validates the new password and confirmation.
3. Hashes the new password.
4. Updates the authenticated user’s record in the authentication database.


## Portal Routes

The portal blueprint does not use a `/dashboard` prefix.

| Route                            | Method      | Purpose                                  |
| -------------------------------- | ----------- | ---------------------------------------- |
| `/`                              | GET         | Portal landing page                      |
| `/updates`                       | GET         | Display alumni update submissions        |
| `/alumni-updates/<edit_id>/edit` | POST        | Save edits to an alumni update           |
| `/class-notes`                   | GET         | Display class note submissions           |
| `/class-notes/<edit_id>/edit`    | POST        | Save edits to a class note               |
| `/memoriam`                      | GET         | Display the memoriam page                |
| `/accounts`                      | GET, POST   | View account details and change password |
| `/login`                         | GET, POST   | Authenticate a staff user                |
| `/logout`                        | GET or POST | End the authenticated session            |

All portal-management pages require authentication.

## Alumni Data Model

The alumni database uses a normalized relational structure.

Core models include:

* `Alumni`
* `AlumniUpdate`
* `AlumniAddress`
* `AlumniFamilyUpdate`
* `AlumniChild`
* `AlumniEmploymentUpdate`
* `AlumniEducationUpdate`
* `AlumniClassNote`

### Alumni Updates

The alumni update workflow can load and edit related data such as:

* alumnus identity and contact information
* address information
* family updates
* children
* employment updates
* additional education
* general life updates
* volunteer interests

The update list uses SQLAlchemy relationship loading to retrieve related records efficiently.

### Class Notes

Class notes are associated with alumni updates and can include:

* first name
* last name
* graduation year
* degree type
* class note text
* image information
* optional display or nameplate information

Edits are applied through model helper methods before the SQLAlchemy session is committed.

## Forms and Validation

Forms use Flask-WTF and WTForms.

The project includes separate forms for:

* login
* password changes
* alumni update editing
* class note editing

CSRF protection is initialized globally through `CSRFProtect`.

Templates should include:

```jinja2
{{ form.hidden_tag() }}
```

inside each POST form.

## Running Tests

The repository contains tests for model mapping and staff authentication behavior.

Install `pytest` if it is not already available:

```powershell
pip install pytest
```

Run the test suite from the project root:

```powershell
pytest
```

For more detailed output:

```powershell
pytest -v
```

Current test files include:

```text
tests/test_model_mapping.py
tests/test_staff_user_model.py
```

## Azure Deployment

The repository includes a GitHub Actions workflow for deploying the application to Azure App Service.

The workflow:

1. Runs when code is pushed to the `main` branch.
2. Can also be started manually with `workflow_dispatch`.
3. Checks out the repository.
4. Configures Python.
5. Creates a virtual environment.
6. Installs dependencies.
7. Packages the application.
8. Deploys the package to the Azure Web App.

The workflow currently targets:

```text
Geneva-App-Portal
```

### Azure Application Settings

Configure the following settings in the Azure App Service environment:

```text
SECRET_KEY
DB_HOST
DB_USER
DB_PASSWORD
ALUMNI_DB_NAME
AUTH_DB_NAME
```

These values should be configured under:

```text
Azure App Service
→ Settings
→ Environment variables
```

Do not place production credentials in the repository or GitHub Actions workflow file.

## Database Schema Changes

The current application initializes Flask-SQLAlchemy but does not currently initialize Flask-Migrate in `app/extensions.py` or `create_app()`.

Therefore, commands such as the following are not available unless Flask-Migrate is added and configured:

```text
flask db migrate
flask db upgrade
```

Until migration support is implemented, database schema changes must be coordinated separately.

To add Flask-Migrate in the future:

1. Add `Flask-Migrate` to `requirements.txt`.
2. Create a `Migrate()` extension.
3. Initialize it with `migrate.init_app(app, db)`.
4. Create or restore the Alembic migration directory.
5. Confirm that migrations work correctly with both SQLAlchemy binds.

## Development Workflow

A typical development workflow is:

```powershell
git checkout -b feature/description
```

Make and test the changes:

```powershell
pytest
python run.py
```

Commit the work:

```powershell
git add .
git commit -m "Describe the change"
git push origin feature/description
```

Then open a pull request into `main`.

Because pushes to `main` trigger the Azure deployment workflow, changes should be reviewed and tested before merging.
