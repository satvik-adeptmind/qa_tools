import os
from urllib.parse import urlencode


_ENV_KEYS = {
    "prod": "ADEPT_SEARCH_PROD_ENDPOINT",
    "staging": "ADEPT_SEARCH_STAGING_ENDPOINT",
}

_SECRET_KEYS = {
    "prod": "search_prod_endpoint",
    "staging": "search_staging_endpoint",
}


def _normalize_environment(environment: str) -> str:
    env = (environment or "prod").strip().lower()
    if env in {"production", "prod"}:
        return "prod"
    if env in {"preprod", "pre-prod", "stage", "staging"}:
        return "staging"
    raise ValueError(f"Unsupported environment '{environment}'. Use 'prod' or 'staging'.")


def resolve_search_base_endpoint(environment: str, secrets=None) -> str:
    """
    Resolve search API base endpoint from Streamlit secrets or environment variables.

    Supported setup:
    - Streamlit secrets:
        [api_endpoints]
        search_prod_endpoint = "https://.../search"
        search_staging_endpoint = "https://.../search"
    - Env vars:
        ADEPT_SEARCH_PROD_ENDPOINT
        ADEPT_SEARCH_STAGING_ENDPOINT
    """
    env = _normalize_environment(environment)

    if secrets is not None:
        try:
            api_endpoints = secrets.get("api_endpoints")
            if api_endpoints and api_endpoints.get(_SECRET_KEYS[env]):
                return str(api_endpoints.get(_SECRET_KEYS[env])).strip()
            if secrets.get(_SECRET_KEYS[env]):
                return str(secrets.get(_SECRET_KEYS[env])).strip()
        except Exception:
            pass

    endpoint = os.getenv(_ENV_KEYS[env], "").strip()
    if endpoint:
        return endpoint

    raise ValueError(
        f"Search endpoint is not configured for '{env}'. "
        f"Set Streamlit secrets api_endpoints.{_SECRET_KEYS[env]} or env var {_ENV_KEYS[env]}."
    )


def build_search_url(environment: str, shop_id: str, secrets=None) -> str:
    endpoint = resolve_search_base_endpoint(environment=environment, secrets=secrets)
    query = urlencode({"shop_id": (shop_id or "").strip()})
    separator = "&" if "?" in endpoint else "?"
    return f"{endpoint}{separator}{query}"

