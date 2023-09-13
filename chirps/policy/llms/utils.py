"""Utility functions for LLMs."""
import tiktoken

GENERATIVE_MODELS = {
    'OpenAI': ['gpt-4-0613'],
    'anthropic': ['claude-2'],
}

DEFAULT_SERVICE = 'OpenAI'
DEFAULT_MODEL = 'gpt-4-0613'
MAX_TOKENS = 4096


def get_generative_services() -> list[str]:
    """Return a list of generative services."""
    return list(GENERATIVE_MODELS.keys())


def get_generative_models_for_service(service: str) -> list[str]:
    """Return a list of generative models for a given service."""
    return GENERATIVE_MODELS.get(service, [])


def get_generative_service_from_model(model: str) -> str:
    """Return the service for a given model."""
    for service, models in GENERATIVE_MODELS.items():
        if model in models:
            return service

    return ''


def num_tokens_from_messages(messages, model=DEFAULT_MODEL):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding('cl100k_base')
    if model == DEFAULT_MODEL:  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += len(encoding.encode(message.content))
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens

    return 0
