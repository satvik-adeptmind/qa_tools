from .base_parser import BaseParser

class AnnTaylorParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        """
        Parses the API response to extract specified product details.

        This method processes the 'products' list from the api_data payload.
        For each product, it extracts a predefined set of fields and formats
        them into a structured string.

        Args:
            search_keyword (str): The original search term used for the API call.
            api_data (dict): The JSON data returned from the API.

        Returns:
            dict: A dictionary containing the formatted product information
                  or an error message if no products are found.
        """
        products = api_data.get("products", [])
        if not products:
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        
        # A list of the only fields to be extracted from each product.
        fields_to_extract = [
            "title",
            "description",
            "color",
            "fabric_content",
            "pant_fit",
            "waistband",
            "dress_style",
            "legshape_type",
            "size_type"
        ]

        for i, product in enumerate(products):
            # Start building the formatted string for the current product.
            product_details = [f"prod {i + 1}:"]
            
            # Loop through the desired fields and pull their values from the product data.
            for field in fields_to_extract:
                # Safely get the value using .get(), defaulting to 'N/A'.
                # The .strip() method is called on strings to clean up whitespace.
                value = product.get(field, 'N/A')
                if isinstance(value, str):
                    value = value.strip()
                
                # Append the field and its value to our list, ensuring empty values are handled.
                product_details.append(f"{field}: {value or 'N/A'}")
            
            # Combine the collected details into a single string with newline separators.
            llm_texts.append("\n".join(product_details))
            
        return self._format_llm_output(search_keyword, llm_texts)