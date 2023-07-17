# Chirps

Chirps is a Django-based Python web application that allows users to search and scan vector databases for sensitive data. The application can connect to [Mantium] (https://mantiumai.com/) applications and to vector databases like Redis and Pinecone. Users can create and manage scanning plans, execute scans against a target using a selected plan, and view the results of the scan, including any findings.

## Quick Start

- `pip install -r requirements.txt`
- Navigate to /chirps and run `./manage.py initialize_app` to start the application and necessary services

## Development - Getting Started

Install required Python modules with `pip install -r requirements.txt`.

### `manage.py`

All of the functionality you need is handled with Django's `manage.py` interface. It's executable, and can be found in the `chirps` subdirectory. Always run `manage.py` from within the chirps subdirectory. Okay.

### Database Schema

Initialize your database (sqlite) by executing `./manage.py migrate`. This will create all of your tables. Generate new migrations by executing `./manage.py makemigrations`. Running the `migrate` command again will apply the migration(s).

### Database fixtures

Pre-populate the database with some default data (plans) by executing `./manage.py loaddata <path/to/fixture>.json`

### Start Services

The chirps application makes use of Celery and RabbitMQ for job processing. Executing a scan, the scan task will be offloaded to Celery for async processing. In order to start those two components execute the following commands:

- `./manage.py rabbitmq --start`
- `./manage.py celery --start`

Both the rabbitmq and celery commands have `--stop` and `--restart` options as well.

#### IMPORTANT CELERY TIP

If you make changes to a Celery task, it must be restarted in order for those changes to be picked up. Simply run
`./manage.py celery --restart`

### Run Webserver

`./manage.py runserver`

This will fire up the Django development server. Connect to the URL that it outputs in the console.

### Run Tests

Once in a while, you might right a test (bravo!). Those can be executed by running `./manage.py test`.

### Run Documentation Server

The `/docs` folder contains documentation which is built via [Jekyll](https://jekyllrb.com/). In order to run the local development server, execute `bundle exec jekyll serve`.

## Project Layout

At a high level, chirps performs security scans on vector databases and knowledge query systems. Users choose a `Plan` to `Scan` a `Target`.

### `Target`

The `Target` application allows users to interact with Mantium applications and vector databases like Redis and Pinecone for storing and searching document embeddings. Users can create, edit, and delete target configurations, which include connection details and authentication credentials. Each target model is derived from a `BaseTarget` model that implements the `search()` and `test_connection()` methods for seamless integration with different services/databases.

### `Scan`

The `Scan` application manages scans and their results. Users can create, execute, and analyze scans using plans with defined rules. Users can also review scan findings.

### `Plan`

The `Plan` application manages scanning plans and rules for the Scan application. A Plan consists of a set of rules that define the steps executed when scanning a target. Users can create plans or use preloaded templates.

### `Authentication System`

The authentication system in this Django-based Python web application manages user authentication and account features. Users can sign up, log in, and update their profiles, including an optional OpenAI API key, which is hashed before saving.

The `Profile` model extends Django's built-in User model with a one-to-one relationship and includes an `openai_key` field. Forms such as `ProfileForm`, `LoginForm`, and `SignupForm` handle user profile updates, logins, and registrations, with custom methods like `clean_openai_key()` for hashing the OpenAI API key.
