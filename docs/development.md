---
layout: menu
title: Development
permalink: /development/
---

# Architecture
![Architecture]({{"/assets/images/Application Architecture.png" | relative_url }})

The Chirps application will execute scans against a taget.

## What is in a Scan?
A scan executes a plan against an asset. A plan is a list of rules. Each rule has a query which is executed against the asset. The rule has a match regular expression that will be used to search the results of the query. If a match is found, it is flagged.

When a user kicks off a scan, a Celery task is queued. The scan task, found in `./scan/tasks.py`, will iterate through each rule in a plan, executing the queries against the scan asset. Results are stored in the database via the `Result` and `Finding` models.

## What are Targets?
A asset is a destination that rule queries are executed against. Target providers are responsible for executing the queries and handing back the results to the scan task.


# Plan Application

The Plan application provides functionality for managing scanning plans and rules. A Plan consists of a set of rules that define the steps to be executed when scanning an asset. Plans can be created by users or preloaded as templates.

## Models

### Plan

The `Plan` model represents a scanning plan. It contains the following fields:

- `name`: A CharField with a maximum length of 256 characters.
- `description`: A TextField for storing a detailed description of the plan.
- `is_template`: A BooleanField indicating whether the plan is a template for other plans.
- `user`: A ForeignKey to the User model, binding the plan to a specific user if it isn't a template. This field is nullable and can be left blank.

### Rule

The `Rule` model represents a step to be executed within a plan. It contains the following fields:

- `name`: A CharField with a maximum length of 256 characters.
- `description`: A TextField for storing a detailed description of the rule.
- `query_string`: A TextField for storing the query to be run against the asset.
- `query_embedding`: A TextField for storing the embedding of the query string. This field is nullable and can be left blank.
- `regex_test`: A TextField for storing the regular expression to be run against the response documents.
- `severity`: An IntegerField indicating the severity of the problem if the regex test finds results in the response documents.
- `plan`: A ForeignKey to the Plan model, indicating the plan this rule belongs to.

## Views

### dashboard

The `dashboard` view renders the dashboard for the Plan application. It fetches a list of all available template plans and paginates the results, displaying a default of 25 plans per page.

### create

The `create` view renders the form for creating a new plan.

## Loading Plans from JSON Files

Plans can be loaded from JSON files stored in the `fixtures/plans` directory. All plans are automatically loaded when running the `./manage.py initialize_app` command. To load a new plan added to the fixtures directory, use the following command:

`./manage.py loaddata /plan/fixtures/plan/<new_plan>.json`


# Scan Application

## Overview

The Scan application provides functionality for managing scans and their results. Scans are executed against an asset using a selected plan, which consists of a set of rules. The results of the scan include the findings for each rule.

## Models

### Scan

The `Scan` model represents a single scan run against an asset. It contains the following fields:

- `started_at`: A DateTimeField indicating the start time of the scan.
- `finished_at`: A DateTimeField indicating the completion time of the scan. This field is nullable.
- `description`: A TextField for storing a description of the scan.
- `plan`: A ForeignKey to the Plan model.
- `asset`: A ForeignKey to the BaseTarget model.
- `celery_task_id`: A CharField with a maximum length of 256 characters, used for storing the associated Celery task ID. This field is nullable.
- `progress`: An IntegerField for storing the progress percentage of the scan.
- `user`: A ForeignKey to the User model, indicating the user who initiated the scan. This field is nullable.

### Result

The `Result` model represents a single result from a rule. It contains the following fields:

- `scan`: A ForeignKey to the Scan model.
- `text`: An EncryptedTextField for storing the raw text that was scanned.
- `rule`: A ForeignKey to the Rule model.

### Finding

The `Finding` model identifies the location of a finding within a result. It contains the following fields:

- `result`: A ForeignKey to the Result model.
- `offset`: An IntegerField indicating the starting position of the finding in the result text.
- `length`: An IntegerField indicating the length of the finding in the result text.

## Tasks

### scan_task

The `scan_task` is a Celery task that performs the scan process. It iterates through the plan's rules and executes them against the asset. The results and findings are then persisted in the database.

## Views

### finding_detail

The `finding_detail` view renders the finding detail page. It retrieves a specific finding based on the provided `finding_id`.

### result_detail

The `result_detail` view renders the scan result detail page. It retrieves a specific result based on the provided `result_id`.

### create

The `create` view renders the scan creation page and handles the creation of new scans. When a new scan is created, it kicks off the `scan_task` Celery task.

### dashboard

The `dashboard` view renders the scan dashboard. It displays the user's scans, paginated with a default of 25 scans per page.

### status

The `status` view returns the status of a scan job. It responds with the Celery task status and the progress percentage of the scan.

## in-dev

User-provided scans…

# Target Application

## Overview

The Target application provides functionality for managing and interfacing with various asset databases used for storing and searching document embeddings. The supported asset types include Mantium, Redis, and Pinecone.

## Models

### BaseTarget

The `BaseTarget` model is a polymorphic base class that all asset models inherit from. It contains the following fields:

- `name`: A CharField with a maximum length of 128 characters.
- `user`: A ForeignKey to the User model. This field is nullable.

Each derived asset model should implement the `search()` and `test_connection()` methods.

## Derived Target Models

### MantiumTarget

The `MantiumTarget` model represents a Mantium asset. It contains the following fields:

- `app_id`: A CharField with a maximum length of 256 characters.
- `client_id`: A CharField with a maximum length of 256 characters.
- `client_secret`: An EncryptedCharField with a maximum length of 256 characters.
- `top_k`: An IntegerField with a default value of 100.

### RedisTarget

The `RedisTarget` model represents a Redis asset. It contains the following fields:

- `host`: A CharField with a maximum length of 1048 characters.
- `port`: A PositiveIntegerField.
- `database_name`: A CharField with a maximum length of 256 characters.
- `username`: A CharField with a maximum length of 256 characters.
- `password`: A CharField with a maximum length of 2048 characters. This field is nullable and can be left blank.
- `index_name`: A CharField with a maximum length of 256 characters.
- `text_field`: A CharField with a maximum length of 256 characters.
- `embedding_field`: A CharField with a maximum length of 256 characters.

### PineconeTarget

The `PineconeTarget` model represents a Pinecone asset. It contains the following fields:

- `api_key`: A CustomEncryptedCharField with a maximum length of 256 characters.
- `environment`: A CharField with a maximum length of 256 characters. This field is nullable and can be left blank.
- `index_name`: A CharField with a maximum length of 256 characters. This field is nullable and can be left blank.
- `project_name`: A CharField with a maximum length of 256 characters. This field is nullable and can be left blank.
- `metadata_text_field`: A CharField with a maximum length of 256 characters. This field is nullable.

## Views

### dashboard

The `dashboard` view renders the asset dashboard. It displays the user's assets, paginated with a default of 25 assets per page.

### create

The `create` view renders the asset creation page and handles the creation of new assets.

### ping

The `ping` view tests the connection to a RedisTarget database using the `test_connection()` function.

### delete

The `delete` view deletes an asset from the database.

## Providers

### mantium.py

These files contain the logic for interfacing with each asset type.

# Account Application

## Overview

This Django-based Python web application provides user authentication and account management features. The application allows users to sign up, log in, and update their profile information. The user's profile includes a custom field for storing an OpenAI API key, which is hashed before being saved to the database.

## Models

### Profile

The `Profile` model is a custom user profile model that extends Django's built-in User model with a one-to-one relationship. It contains the following field:

- `openai_key`: A CharField with a maximum length of 100 characters. This field is optional and can be left blank. It is used to store the user's OpenAI API key, which is hashed before being saved to the database.

## Forms

### ProfileForm

`ProfileForm` is a ModelForm for the `Profile` model. It includes a custom method `clean_openai_key()` to hash the OpenAI API key before saving it to the database.

### LoginForm

`LoginForm` is a simple form for handling user logins. It contains two CharFields, `username` and `password`, both with a maximum length of 256 characters.

### SignupForm

`SignupForm` is a form for handling user registration. It includes the following fields:

- `username`: A CharField with a maximum length of 256 characters.
- `email`: An EmailField with a maximum length of 256 characters.
- `password1`: A CharField with a maximum length of 256 characters, displayed as a password input field.
- `password2`: A CharField with a maximum length of 256 characters, displayed as a password input field. This field is used for password confirmation.

## Views

### profile

The `profile` view handles rendering the user's profile page and processing updates to the profile. If the request method is POST, the view updates the user's profile with the submitted data. If the request method is GET, the view renders the profile page with the user's current profile information.

### signup

The `signup` view handles rendering the user registration page and processing new user registrations. If the request method is POST, the view validates the submitted data and creates a new user account and corresponding profile if the data is valid. If the request method is GET, the view renders the registration page.

### login_view

The `login_view` handles rendering the login page and processing user logins. If there are no users in the database, the view redirects to an installation page. If the request method is POST, the view authenticates the user and logs them in if the provided credentials are valid. If the request method is GET, the view renders the login page.
