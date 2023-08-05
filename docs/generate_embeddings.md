# Generate Embeddings Management Command

This Django management command allows you to generate embeddings for policy rules from policy fixtures using a specified service and model.

## Usage

To use the `generate_embeddings` command, follow these steps:

1. Make sure to read and complete the steps outlined in [Getting Started](getting_started.md). The API key for the selected service will be retrieved from the user's profile, so this key should be saved before running this management command.

2. Open a terminal and run the following command:

```sh
python manage.py generate_embeddings
```

4. The command will prompt you to select a service. Available services are displayed with an index number. Enter the number corresponding to your preferred service and press Enter.

5. The command will then prompt you to select a model. Available models for the selected service are displayed with an index number. Enter the number corresponding to your preferred model and press Enter.

6. Enter your Chirps username and password when prompted. The command will authenticate your credentials and use your API key.

7. The command will generate embeddings for the input data using the selected service and model. If an embedding already exists for a specific input, the command will skip it.

## Example

Here's an example of using the `generate_embeddings` command:

```sh
python manage.py generate_embeddings

Output:

1. OpenAI
2. cohere
Enter the number corresponding to your preferred service: 1
1. gpt-3
2. gpt-2
Enter the number corresponding to your preferred model: 1
Enter your Chirps username: testuser
Enter your password: ********

The command will then generate embeddings using the selected service (OpenAI) and model (gpt-3).
```
