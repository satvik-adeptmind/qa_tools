import asyncio
import aiohttp
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

RETRYABLE_EXCEPTIONS = (aiohttp.ClientError, asyncio.TimeoutError)

def get_retry_decorator(max_retries, initial_backoff):
    """Creates a tenacity retry decorator with provided settings."""
    return retry(
        wait=wait_random_exponential(min=initial_backoff, max=60),
        stop=stop_after_attempt(max_retries),
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS)
    )

class ApiClient:
    def __init__(self, retry_config):
        self.retry_decorator = get_retry_decorator(
            retry_config['max_retries'],
            retry_config['initial_backoff']
        )
        self.post = self.retry_decorator(self._post)

    async def _post(self, session, url, headers, payload, timeout):
        """The actual POST request logic."""
        async with session.post(url, headers=headers, json=payload, timeout=timeout) as response:
            response.raise_for_status()
            data = await response.json()
            if data.get("timed_out_services"):
                print(f"Internal API timeout for query '{payload.get('query')}'. Retrying...")
                raise asyncio.TimeoutError("API indicated an internal timeout.")
            return data