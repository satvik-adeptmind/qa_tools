from .base_parser import BaseParser

class JanieAndJackParser(BaseParser):
    """
    A parser for Janie and Jack product data.

    This class is designed to process API responses containing product information
    from Janie and Jack, extracting key details and formatting them for use by a
    large language model (LLM).
    """

    def parse_response(self, search_keyword, api_data):
        """
        Parses the API response to extract and format product information.

        Args:
            search_keyword (str): The original search term used to query the API.
            api_data (dict): The JSON data returned from the product API.

        Returns:
            dict: A formatted dictionary containing the search term and a list
                  of structured product texts, or an error if no products are found.
        """
        products = api_data.get("products", [])
        if not products:
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            details = []

            def add(key, val):
                """A helper function to add a key-value pair to the details list."""
                # Ensure the value is not empty or None before adding
                if val:
                    details.append(f"{key}: {val}")

            # 1. Add basic product attributes
            add("title", product.get("title"))
            add("description", product.get("description"))

            # 2. Add the new specified fields. These are lists in the JSON,
            # so we join them into a comma-separated string.
            add("FABRIC", ", ".join(product.get("FABRIC", [])))
            add("SEASON", ", ".join(product.get("SEASON", [])))
            add("OCCASION", ", ".join(product.get("OCCASION", [])))
            add("VIBE", ", ".join(product.get("VIBE", [])))
            add("LOOK", ", ".join(product.get("LOOK", [])))


            # 3. Extract information from the first variant of the first model
            models = product.get('models', [])
            if models:
                variants = models[0].get('variants', [])
                if variants:
                    first_variant = variants[0]
                    color_val = first_variant.get("color") or first_variant.get("enrichedcolor")
                    add("color", color_val)
                    add("size", first_variant.get("size"))

            # 4. Combine the details for the current product
            if details:
                llm_texts.append(f"prod {i + 1}:\n" + "\n".join(details))

        # 5. Format the final output for the LLM
        return self._format_llm_output(search_keyword, llm_texts)