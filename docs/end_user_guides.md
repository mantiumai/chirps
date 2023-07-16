---
layout: menu
title: End User Guide
permalink: /end-user-guides/
---

# Management Commands

The following management commands allow you to interact with various components of the Chirps application. These commands should be executed from the /chirps subdirectory.

- [Initialize App Command](#initialize-app-command)
- [Start Services Command](#start-services-command)
- [Load Redis Data Command](#load-redis-data-command)
- [Celery Command](#celery-command)
- [RabbitMQ Command](#rabbitmq-command)
- [Redis Command](#redis-command)

## Initialize App Command

The `initialize_app` management command initializes the app by running multiple management commands in succession, such as starting Redis, RabbitMQ, Celery, and running migrations.

### Usage

`./manage.py initialize_app

## Start Services Command

The `start_services` management command starts the services required to run the Chirps application and then starts the development server with `runserver`.

### Usage

`./manage.py start_services`

## Load Redis Data Command

The `load_redis_data` management command loads data from a JSON file into Redis for vector similarity search.

### Usage

python manage.py load_redis_data [file_path] [options]

### Arguments

- `file_path`: Path to the fixtures JSON file.

### Options

- `--index`: Index name to use as a prefix for Redis keys (default: `test`).
- `--host`: Redis host (default: `127.0.0.1`).
- `--port`: Redis port (default: `6379`).
- `--db`: Redis database number (default: `0`).
- `--flushdb`: Flush the Redis database before loading data.

## Celery Command

The `celery` management command allows you to manage a local Celery installation.

### Usage

`./manage.py celery [options]`

### Options

- `--start`: Starts the Celery server.
- `--stop`: Stops the Celery server.
- `--restart`: Restarts the Celery server.

## RabbitMQ Command

The `rabbitmq` management command allows you to interact with the local RabbitMQ development server.

### Usage

`./manage.py rabbitmq [options]

### Options

- `--start`: Starts the RabbitMQ server.
- `--stop`: Stops the RabbitMQ server.
- `--status`: Checks the RabbitMQ server status.

## Redis Command

The `redis` management command allows you to interact with the local Redis development server.

### Usage

`./manage.py redis [options]

### Options

- `--start`: Starts the Redis server.
- `--stop`: Stops the Redis server.
- `--status`: Checks the Redis server status.
