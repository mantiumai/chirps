# chirps

# Development - Getting Started
Install required Python modules with `pip install -r requirements.txt`.

## `manage.py`
All of the functionality you need is handled with Django's `manage.py` interface. It's executable, and can be found in the `chirps` subdirectory. Always run `manage.py` from within the chirps subdirectory.

## Database Schema
Initialize your database (sqlite) by executing `./manage.py migrate`. This will create all of your tables.

## Database fixtures
Pre-populate the database with some default data (plans) by executing `./manage.py loaddata plan/employee.json`

## Start Services
The chirps application makes use of Celery and RabbitMQ for job processing. Executing a scan, the scan task will be offloaded to Celery for async processing. In order to start those two componens execute the following commands:

`./manage.py rabbitmq --start`
`./manage.py celery --start`

Both the rabbitmq and celery commands have `--stop` and `--restart` options as well.

### IMPORTANT CELERY TIP
If you make changes to a Celery task, it must be restarted in order for those changes to be picked up. Simply run
`./manage.py celery --restart`

## Run Webserver
`./manage.py runserver`
This will fire up the Django development server. Connect to the URL that it outputs in the console.

## Run Tests
Once in a while, you might right a test (bravo!). Those can be executed by running `./manage.py test`.

# Project Layout
At a high level, chirps performs security scanas on vector databases and knowlege query systems. Users choose a `Plan` to `Scan` a `Target`.

## `Target`
TBD

## `Scan`
TBD

## `Plan`
TBD

## Authentication System
TBD

## Base Application
TBD
