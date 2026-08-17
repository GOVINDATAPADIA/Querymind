"""Abstracted LLM factory with per-(provider, temperature) caching.

Usage:
    llm = get_llm()                        # default provider + temp=0.0
    llm = get_llm("gemini", temperature=0.7)
    healthy = await check_llm_health()
"""

import asyncio

# pyrefly: ignore [missing-import]
from langchain_openai import ChatOpenAI
# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI
# pyrefly: ignore [missing-import]
from langchain_anthropic import ChatAnthropic
# pyrefly: ignore [missing-import]
from langchain_core.language_models import BaseChatModel
# pyrefly: ignore [missing-import]
from langchain_core.messages import HumanMessage

from config import get_settings

# Module-level cache: (provider, temperature) → LLM instance
_llm_cache: dict[tuple[str, float], BaseChatModel] = {}


def get_llm(
    provider: str | None = None,
    temperature: float = 0.0,
) -> BaseChatModel:
    """Return a cached ``BaseChatModel`` for the given provider and temperature.

    Parameters
    ----------
    provider:
        One of ``"openai"``, ``"gemini"``, ``"claude"``.
        Falls back to ``settings.llm_provider`` when *None*.
    temperature:
        Sampling temperature passed to the model.

    Raises
    ------
    ValueError
        If *provider* is not a recognised string.
    """
    settings = get_settings()
    provider = (provider or settings.llm_provider).lower().strip()

    cache_key = (provider, temperature)
    if cache_key in _llm_cache:
        return _llm_cache[cache_key]

    match provider:
        case "openai":
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=temperature,
                api_key=settings.openai_api_key,
                max_retries=1,
                timeout=30,
            )
        case "gemini":
            llm = ChatGoogleGenerativeAI(
                model="gemini-3.6-flash",
                temperature=temperature,
                google_api_key=settings.google_api_key,
                max_retries=1,
                timeout=30,
            )
        case "claude":
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=temperature,
                api_key=settings.anthropic_api_key,
                max_retries=1,
                default_request_timeout=30,
            )
        case "custom":
            llm = ChatOpenAI(
                model=settings.custom_llm_model,
                temperature=temperature,
                api_key=settings.custom_llm_api_key,
                base_url=settings.custom_llm_base_url,
                max_retries=1,
                timeout=30,
            )
        case _:
            raise ValueError(
                f"Unknown LLM provider '{provider}'. "
                "Supported: openai, gemini, claude, custom."
            )

    _llm_cache[cache_key] = llm
    return llm


async def check_llm_health() -> bool:
    """Quick check if LLM configuration / API key is present."""
    settings = get_settings()
    if settings.llm_provider == "gemini":
        return bool(settings.google_api_key)
    elif settings.llm_provider == "custom":
        return bool(settings.custom_llm_api_key)
    elif settings.llm_provider == "openai":
        return bool(settings.openai_api_key)
    elif settings.llm_provider == "claude":
        return bool(settings.anthropic_api_key)
    return True
