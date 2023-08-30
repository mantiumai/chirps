import tiktoken

from .agents import DEFAULT_MODEL


def num_tokens_from_messages(messages, model=DEFAULT_MODEL):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding('cl100k_base')
    if model == 'gpt-3.5-turbo-0613':  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += len(encoding.encode(message.content))
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens

    return 0
