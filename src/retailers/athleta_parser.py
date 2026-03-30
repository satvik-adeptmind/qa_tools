from .base_parser import BaseParser

class AthletaParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        """
        Parses the API response from Athleta to extract specified product details.

        This method processes the 'products' list from the api_data payload.
        For each product, it extracts a predefined set of attributes. It handles
        both simple string fields and fields that are lists of strings, which
        are converted to a single comma-separated string.

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
        for i, product in enumerate(products):
            # --- Extract Simple String Fields ---
            title = product.get('title', 'N/A').strip() or 'N/A'
            description = product.get('description', 'N/A').strip() or 'N/A'
            
            # --- Handle List-Based Fields ---
            # Helper function to safely process fields that are lists
            def get_list_as_string(field_name):
                items = product.get(field_name, [])
                if items and isinstance(items, list):
                    return ", ".join(items)
                return "N/A"

            # Format the list of bullets into a readable, multi-line string
            bullets_list = product.get('bullets', [])
            bullets = "\n".join([f"- {bullet}" for bullet in bullets_list]) if bullets_list else "N/A"

            # Extract and format the other list-based fields
            available_colors = get_list_as_string('ALL_VARIANT_COLORS')
            fit_type = get_list_as_string('FIT_TYPE')
            neckline = get_list_as_string('NECKLINE')
            fabric = get_list_as_string('FABRIC')
            occasion = get_list_as_string('OCCASION')
            sports_type = get_list_as_string('SPORTS_TYPE')
            age = get_list_as_string('AGE')
            
            # --- Assemble the final formatted text for the product ---
            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {description}
available_colors: {available_colors}
fit_type: {fit_type}
neckline: {neckline}
fabric: {fabric}
occasion: {occasion}
sports_type: {sports_type}
age: {age}
bullets:
{bullets}""")

        return self._format_llm_output(search_keyword, llm_texts)