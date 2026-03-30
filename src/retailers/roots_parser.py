from .base_parser import BaseParser

class RootsParser(BaseParser):
    """
    A parser designed to extract product information from a 'Roots' API response payload.
    
    This parser handles the specific nested structure of the Roots data, extracting
    details from both the top-level and the nested 'attributes' dictionary. It correctly
    processes attributes that may have single or multiple values.
    """
    
    def _get_joined_attribute(self, attributes, key, separator=' / '):
        """
        Safely retrieves an attribute's value(s) and joins them into a single string.
        Handles cases where the attribute is a list or a single value.
        """
        value = attributes.get(key)
        if isinstance(value, list) and value:
            # Join all items in the list
            return separator.join(map(str, value))
        elif value:
            # If it's not a list but has a value, return it as a string
            return str(value)
        return 'N/A'

    def parse_response(self, search_keyword, api_data):
        """
        Parses the API response data to extract and format product information.

        Args:
            search_keyword (str): The original search term.
            api_data (dict): The JSON data returned from the API.

        Returns:
            dict: A dictionary formatted for a Large Language Model (LLM),
                  containing the structured product data or an error message.
        """
        # If the top-level object is a single product, wrap it in a list for consistent processing
        products = [api_data] if "prod_id" in api_data else api_data.get("products", [])
            
        if not products:
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            # Extract title and description from the top level
            title = product.get('title', 'N/A').strip() or 'N/A'
            desc = product.get('description', 'N/A').strip() or 'N/A'
            
            # Get the nested attributes dictionary for easier access
            attributes = product.get('attributes', {})
            
            # Extract details from the nested 'attributes' dictionary using the corrected helper
            age = self._get_joined_attribute(attributes, 'AGE')
            gender = self._get_joined_attribute(attributes, 'GENDER')
            occasion = self._get_joined_attribute(attributes, 'OCCASION')
            sleeve_type = self._get_joined_attribute(attributes, 'SLEEVE_TYPE')
            sports_type = self._get_joined_attribute(attributes, 'SPORTS_TYPE')
            fabric = self._get_joined_attribute(attributes, 'FABRIC', separator=', ') # Using comma for fabric
            
            # Get all available colors and join them with a slash
            all_colors = self._get_joined_attribute(attributes, 'ALL_VARIANT_COLORS')
            
            # Format the extracted data into a single string for the LLM
            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {desc}
age: {age}
gender: {gender}
occasion: {occasion}
sleeve_type: {sleeve_type}
fabric: {fabric}
sports_type: {sports_type}
colors: {all_colors}""")
            
        return self._format_llm_output(search_keyword, llm_texts)