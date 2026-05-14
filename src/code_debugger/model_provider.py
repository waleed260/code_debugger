"""
Shared model provider configuration for OpenAI Agents SDK.

Registers OpenRouter provider prefixes so model names like
`meta-llama/llama-3.3-70b-instruct:free` work correctly with the SDK.
"""

from agents import RunConfig
from agents.models.multi_provider import MultiProvider, MultiProviderMap
from agents.models.openai_provider import OpenAIProvider

_registered = False
_cached_config = None

OPENROUTER_PREFIXES = [
    'meta-llama', 'google', 'mistralai', 'deepseek', 'qwen',
    'anthropic', 'cohere', 'ai21', 'nvidia', 'x-ai',
    'perplexity', 'grok', 'openai', 'azure', 'cerebras',
    'together', 'fireworks', 'groq', 'replicate', 'sophosympatheia',
]


def get_run_config() -> RunConfig:
    global _registered, _cached_config
    if _cached_config is not None:
        return _cached_config

    provider_map = MultiProviderMap()
    for prefix in OPENROUTER_PREFIXES:
        provider_map.add_provider(prefix, OpenAIProvider())

    model_provider = MultiProvider(provider_map=provider_map)
    _cached_config = RunConfig(model_provider=model_provider)
    return _cached_config
