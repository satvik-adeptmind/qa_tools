from abc import ABC, abstractmethod

BASE_URL = "https://search-prod-dlp-adept-search.search-prod.adeptmind.app/search"

class BaseParser(ABC):
    """Abstract Base Class defining the interface for all retailer-specific parsers."""
    def __init__(self, config):
        self.config = config

    def build_request(self, search_keyword):
        """
        Default request builder. Uses the centralized BASE_URL.
        Can be overridden by subclasses if a retailer has a unique URL structure.
        """
        url_with_shop = f"{BASE_URL}?shop_id={self.config['shop_id']}"
        payload = {
            "query": search_keyword,
            "size": self.config['api_settings']['result_size'],
            "force_exploding_variants": self.config.get('parser_settings', {}).get('force_exploding_variants', False),
        }
        return (url_with_shop, payload)

    @abstractmethod
    def parse_response(self, search_keyword, api_response_data):
        """Parses the JSON data from the API and formats it."""
        pass

    def _format_llm_output(self, search_keyword, formatted_texts):
        """Helper to create the final string output."""
        final_output = f"search term: {search_keyword}\n\n" + "\n\n".join(formatted_texts)
        return {"search_term": search_keyword, "llm_formatted_output": final_output}