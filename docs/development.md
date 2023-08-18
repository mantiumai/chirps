---
layout: menu
title: Development
permalink: /development/
---

# Architecture
![Architecture]({{"/assets/images/application_architecture.png" | relative_url }})

The Chirps application will execute scans against a taget.

## What is in a Scan?
A scan executes one or more policies against one or more assets. A policy is a list of rules. Each rule has a query which is executed against the asset(s). The rule has a match regular expression that will be used to search the results of the query. If a match is found, it is flagged.

When a user kicks off a scan, a Celery task is queued. If multiple assets are selected, multiple tasks are queued. The scan task, found in `./scan/tasks.py`, will iterate through each rule in a policy, executing the queries against the scan asset. Results are stored in the database via the `Result` and `Finding` models.

## What are Assets?
An asset is a destination that rule queries are executed against. Asset providers are responsible for executing the queries and handing back the results to the scan task.


# Policy Application

The Policy application provides functionality for managing scanning policies and rules. A Policy consists of a set of rules that define the steps to be executed when scanning an asset. Policies can be created by users or preloaded as templates.

## Models

### Policy

The `Policy` model represents a scanning policy. It contains the following fields:

- `name`: A CharField with a maximum length of 256 characters.
- `description`: A TextField for storing a detailed description of the policy.
- `is_template`: A BooleanField indicating whether the policy is a template for other policies.
- `user`: A ForeignKey to the User model, binding the policy to a specific user if it isn't a template. This field is nullable and can be left blank.
- `archived`: A BooleanField indicating whether the policy has been archived.
- `current_version`: A ForeignKey to the PolicyVersion model, binding the policy to a specific version. This field is nullable and can be left blank.

### PolicyVersion
The `PolicyVersion` model represents a particular version of a Policy. It contains the following fields:

- `number`: An IntegerField that keeps track of the policy's version.
- `created_at`: A DateTimeField indicating when the PolicyVersion was created.
- `policy`: A ForeignKey to the Policy model.

### Rule

The `Rule` model represents a step to be executed within a policy. It contains the following fields:

- `name`: A CharField with a maximum length of 256 characters.
- `query_string`: A TextField for storing the query to be run against the asset.
- `query_embedding`: A TextField for storing the embedding of the query string. This field is nullable and can be left blank.
- `regex_test`: A TextField for storing the regular expression to be run against the response documents.
- `severity`: An IntegerField indicating the severity of the problem if the regex test finds results in the response documents.
- `policy`: A ForeignKey to the Policy model, indicating the policy this rule belongs to.

## Views

### dashboard

The `dashboard` view renders the dashboard for the Policy application. It fetches a list of all available template policies and paginates the results, displaying a default of 25 policies per page.

### create

The `create` view renders the form for creating a new policy.

## Loading Policies from JSON Files

Policies can be loaded from JSON files stored in the `fixtures/policy` directory. All policies are automatically loaded when running the `./manage.py initialize_app` command. To load a new policy added to the fixtures directory, use the following command:

`./manage.py loaddata /policy/fixtures/policy/<new_plan>.json`


# Scan Application

## Overview

The Scan application provides functionality for managing scans and their results. Scans are executed against one or more assets using selected policies, each of which consists of a set of rules. The results of the scan include the findings for each rule.

## Models

### Scan

The `Scan` model represents a single scan run against an asset. It contains the following fields:

- `started_at`: A DateTimeField indicating the start time of the scan, automatically set when the scan is created.
- `finished_at`: A DateTimeField indicating the completion time of the scan. This field is nullable.
- `description`: A TextField for storing a description of the scan.
- `policies`: A ManyToManyField to the Policy model.
- `celery_task_id`: A CharField with a maximum length of 256 characters, used for storing the associated Celery task ID. This field is nullable.
- `user`: A ForeignKey to the User model, indicating the user who initiated the scan. This field is nullable.
- `status`: A CharField with a maximum length of 32 characters, storing the status of the scan. The options are 'Queued', 'Running', 'Complete', 'Failed', with 'Queued' being the default.

Additional methods of `Scan` model:
- `__str__`: Returns the description of the scan.
- `progress`: Computes the progress of the scan.
- `duration`: Calculates the duration the scan has run.
- `asset_count`: Fetches the number of scan assets associated with this scan.
- `findings_count`: Fetches the number of findings associated with this scan.

### ScanAsset

The `ScanAsset` model represents a single asset that was scanned. It contains the following fields:

- `started_at`: A DateTimeField indicating the start time of the scan of the asset, automatically set when the scan is created.
- `finished_at`: A DateTimeField indicating the completion time of the scan of the asset. This field is nullable.
- `scan`: A ForeignKey to the Scan model, with the related name 'scan_run_assets'.
- `asset`: A ForeignKey to the BaseAsset model.
- `celery_task_id`: A CharField with a maximum length of 256 characters, used for storing the associated Celery task ID. This field is nullable.
- `progress`: An IntegerField for storing the progress percentage of the scan of the asset, with a default of 0.

Additional methods of `ScanAsset` model:
- `__str__`: Returns the name of the asset.
- `celery_task_status`: Fetches the status of the Celery task associated with this scan.
- `celery_task_output`: Fetches the output of the Celery task associated with this scan.

### Result

The `Result` model represents a single result from a rule. It contains the following fields:

- `scan_asset`: A ForeignKey to the ScanAsset model, with the related name 'results'.
- `text`: An EncryptedTextField for storing the raw text that was scanned.
- `rule`: A ForeignKey to the Rule model.

Additional methods of `Result` model:
- `has_findings`: Returns True if the result has findings, False otherwise.
- `findings_count`: Returns the number of findings associated with this result.
- `__str__`: Returns the rule name and scan ID as a string.

### Finding

The `Finding` model identifies the location of a finding within a result. It contains the following fields:

- `result`: A ForeignKey to the Result model, with the related name 'findings'.
- `offset`: An IntegerField indicating the starting position of the finding in the result text.
- `length`: An IntegerField indicating the length of the finding in the result text.

Additional methods of `Finding` model:
- `__str__`: Returns the offset and length as a string, separated by a colon.
- `text`: Returns the text of the finding.
- `surrounding_text`: Returns the text of the finding, with some surrounding context, highlighted with the 'text-danger' CSS class.
- `with_highlight`: Returns the entire text searched by the finding's rule, with the finding highlighted with the 'bg-danger text-white' CSS class.


## Tasks

### scan_task

The `scan_task` is a Celery task that performs the scan process. It iterates through a policy's rules and executes them against the asset. The results and findings are then persisted in the database.

## Views

### finding_detail

The `finding_detail` view renders the finding detail page. It retrieves a specific finding based on the provided `finding_id`.

### result_detail

The `result_detail` view renders the scan result detail page. It retrieves specific results based on the provided `scan_id`, `policy_id`, and `rule_id`.

### view_scan

The `view_scan` view renders the details for a particular scan based on the provided `scan_id`. It aggregates the results and findings of the scan, as well as the severity count for display on the scan detail page.

### create

The `create` view renders the scan creation page and handles the creation of new scans. When a new scan is created, it initiates a `scan_task` Celery task for each selected asset.

### dashboard

The `dashboard` view renders the scan dashboard. It displays the user's scans, paginated with a default of 25 scans per page.

### status

The `status` view returns the status of a scan job. It responds with the Celery task status and the progress percentage of the scan.

### asset_status

The `asset_status` view returns the status of a particular scan asset job. It responds with the Celery task status and the progress percentage of the scan asset.

### findings_count

The `findings_count` view returns the number of findings associated with a particular scan. The response is the count of findings for the scan.


# Asset Application

## Overview

The Asset application provides functionality for managing and interfacing with various vector database services used for storing and searching document embeddings. The supported asset types include Mantium, Redis, and Pinecone.

## Models

### BaseAsset

The `BaseAsset` model is a polymorphic base class that all asset models inherit from. It contains the following fields:

- `name`: A CharField with a maximum length of 128 characters.
- `user`: A ForeignKey to the User model. On delete, it follows the cascade strategy. This field is nullable.
- `html_logo`: This is a string field used to define a path to the logo of the asset. The path should be within the static directory. It defaults to None.
- `REQUIRES_EMBEDDINGS`: This is a boolean field used to indicate whether or not the model requires embeddings. It defaults to False.

Each derived asset model should implement the `search()`, `test_connection()`, and `logo_url()` methods.

The `logo_url()` method fetches the logo URL for the asset.

### Derived Asset Models

#### MantiumAsset

The `MantiumAsset` model represents a Mantium asset. It contains the following fields:

- `app_id`: A CharField with a maximum length of 256 characters.
- `client_id`: A CharField with a maximum length of 256 characters.
- `client_secret`: An EncryptedCharField with a maximum length of 256 characters.
- `top_k`: An IntegerField with a default value of 100.
- `html_logo`: A string field that represents the path to the logo of the Mantium asset. The path should be within the static directory.
- `html_name`: A string field that stores the name of the Mantium asset.
- `html_description`: A string field that stores a description of the Mantium asset.

The `search()` method performs a vector database search against the Mantium asset.

#### PineconeAsset

The `PineconeAsset` model represents a Pinecone asset. It contains the following fields:

- `api_key`: An EncryptedCharField with a maximum length of 256 characters. This field is editable.
- `environment`: A CharField with a maximum length of 256 characters. This field is nullable and can be left blank.
- `index_name`: A CharField with a maximum length of 256 characters. This field is nullable and can be left blank.
- `project_name`: A CharField with a maximum length of 256 characters. This field is nullable and can be left blank.
- `metadata_text_field`: A CharField with a maximum length of 256 characters. This field is not nullable.
- `embedding_model`: A CharField with a default value of 'text-embedding-ada-002' and a maximum length of 256 characters.
- `embedding_model_service`: A CharField with a default value of 'OpenAI' and a maximum length of 256 characters.
- `html_logo`: A string field that represents the path to the logo of the Pinecone asset. The path should be within the static directory.
- `html_name`: A string field that stores the name of the Pinecone asset.
- `html_description`: A string field that stores a description of the Pinecone asset.

The `search()` method performs a search against the Pinecone asset.

#### RedisAsset

The `RedisAsset` model represents a Redis asset. It contains the following fields:

- `host`: A CharField with a maximum length of 1048 characters.
- `port`: A PositiveIntegerField.
- `database_name`: A CharField with a maximum length of 256 characters.
- `username`: A CharField with a maximum length of 256 characters.
- `password`: A CharField with a maximum length of 2048 characters. This field is nullable and can be left blank.
- `index_name`: A CharField with a maximum length of 256 characters.
- `text_field`: A CharField with a maximum length of 256 characters.
- `embedding_field`: A CharField with a maximum length of 256 characters.
- `embedding_model`: A CharField with a default value of 'text-embedding-ada-002' and a maximum length of 256 characters.
- `embedding_model_service`: A CharField with a default value of 'OpenAI' and a maximum length of 256 characters.
- `html_logo`: A string field that represents the path to the logo of the Redis asset. The path should be within the static directory.
- `html_name`: A string field that stores the name of the Redis asset.
- `html_description`: A string field that stores a description of the Redis asset.

The `search()` method performs a search against the Redis asset.

## Views

### dashboard

The `dashboard` view renders the asset dashboard. It displays the user's assets, paginated with a default of 25 assets per page.

### create

The `create` view renders the asset creation page and handles the creation of new assets.

### ping

The `ping` view tests the connection to a RedisAsset database using the `test_connection()` function.

### delete

The `delete` view deletes an asset from the database.

## Providers

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
