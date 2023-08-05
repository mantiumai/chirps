# Generate Embeddings Management Command

This Django management command allows you to generate embeddings for policy rules from policy fixtures using a specified service and model.

## Usage

To use the `generate_embeddings` command, follow these steps:

1. Make sure to read and complete the steps outlined in [Getting Started](getting_started.md).

2. Save the API key for the selected service. It will be retrieved from your profile after providing login credentials. The API key should be saved before running this management command.

2. Open a terminal and run the following command:

```sh
python manage.py generate_embeddings
```

4. The command will prompt you to select a service. Available services are displayed with an index number. Enter the number corresponding to your preferred service and press Enter.

5. The command will then prompt you to select a model. Available models for the selected service are displayed with an index number. Enter the number corresponding to your preferred model and press Enter.

6. Enter your Chirps username and password when prompted. The command will authenticate your credentials and use your API key.

Embeddings are then generated for the input data using the selected service and model. An embedding is generated if one does not already exist for any combination of service/model/rules. The command will skip the rule if an embedding already exists.

## Example

Here's an example of using the `generate_embeddings` command:

```sh
chirps $ ./manage.py generate_embeddings
1. cohere
2. OpenAI
Enter the number corresponding to your preferred service: 2
Selected option: OpenAI
1. text-embedding-ada-002
Enter the number corresponding to your preferred model: 1
Selected option: text-embedding-ada-002
Enter your Chirps username:
Enter your password:

...

The command will then generate embeddings using the selected service (OpenAI) and model (gpt-3).
```
