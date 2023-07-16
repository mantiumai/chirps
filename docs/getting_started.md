---
layout: page
title: Getting Started
permalink: /getting-started/
---

Chirps is a Django-based Python web application that allows users to search and scan vector databases for sensitive data. The application can connect to Mantium applications and to vector databases like Redis and Pinecone. Users can create and manage scanning plans, execute scans against a target using a selected plan, and view the results of the scan, including any findings.

## Project Layout

At a high level, chirps performs security scans on vector databases and knowledge query systems. Users choose a `Plan` to `Scan` a `Target`.

### `Target`

The `Target` application allows users to interact with Mantium applications and vector databases like Redis and Pinecone for storing and searching document embeddings. Users can create, edit, and delete target configurations, which include connection details and authentication credentials. Each target model is derived from a `BaseTarget` model that implements the `search()` and `test_connection()` methods for seamless integration with different database types.

### `Scan`

The `Scan` application manages scans and their results for Mantium applications and vector databases like Redis and Pinecone. Users can create, execute, and analyze scans using plans with defined rules, and review scan findings.
The application includes models for scans, results, and findings, with fields to store relevant information. The `scan_task` Celery task performs the scan process, executing rules against targets and saving results in

### `Plan`

The `Plan` application manages scanning plans and rules for the Scan application. A Plan consists of a set of rules that define the steps executed when scanning a target. Users can create plans or use preloaded templates.

### `Authentication System`

The authentication system in this Django-based Python web application manages user authentication and account features. Users can sign up, log in, and update their profiles, including an optional OpenAI API key, which is hashed before saving.

The `Profile` model extends Django's built-in User model with a one-to-one relationship and includes an `openai_key` field. Forms such as `ProfileForm`, `LoginForm`, and `SignupForm` handle user profile updates, logins, and registrations, with custom methods like `clean_openai_key()` for hashing the OpenAI API key.

## Getting Started with GitHub Codespaces

1. Click the green "Code" button on your forked repository and choose "Open with Codespaces."
2. Click "New codespace" to create a new codespace for the project.
3. Wait for the codespace to be created and the dependencies to be installed. Expect this first build to take at least 10 minutes. Codespace rebuilds should be much faster.

## Quick Start

- `pip install -r requirements.txt`
- Navigate to /chirps and run `./manage.py initialize_app`
- When prompted, create a superuser profile
- In the codespace, click "Ports" on the lower toolbar and click the link under "Forwarded Ports" to access the application at port 8000.

### Target Configuration
Now that Chirps is running, it's time to setup your first target. Click on the `targets` top level menu. From the targets dashboard, click the `new` button and select your target type. As of this writing, Redis, Pinecone, and Mantium are supported. On the target configuration page, enter the details which will allow Chirps to perform queries against it.

### Plan Configuration
Chirps ships with a few stock plans. If you'd like to customize them, or create one from scratch, click on the `plans` top level menu. From the tempaltes tab, open a plan that you'd like to work with. Click on the `clone` button. For each rule in the plan, you must specify:
- The query string to send to the target
- A regular expression to execute against query results. If this matches something, a result finding will be saved.
- The severity is a user-configured value to determine how important any finding is which matches the rule.

### Your First Scan
With a target and plan ready, it's time to execute a scan. Navigate to the scan dashboard by clicking the `scan` button in the top navbar. From the scan dashboad, click the `new` button. On the new scan page, select the plan to run, and the target to execute the plan against. Click `create` to start the scan.

## Debugging Failed Tasks
Task logs are written to `/var/log/celery/`. View the worker log file (`w1-1.log`) to uncover any issues.
