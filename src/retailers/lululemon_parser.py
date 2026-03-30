from .base_parser import BaseParser

class LululemonParser(BaseParser):
    """
    A parser for processing product data from a Lululemon API response.

    This class extracts detailed product information from the JSON payload,
    including a list of all variant colors for each product, formats it into a 
    structured text format for a language model, and handles cases where 
    product data may be missing or incomplete.
    """
    def parse_response(self, search_keyword, api_data):
        """
        Parses the API response to extract and format product data.

        Args:
            search_keyword (str): The original search term used for the API query.
            api_data (dict): The JSON data returned from the API, expected to
                             contain a 'products' list.

        Returns:
            dict: A dictionary formatted for the LLM, containing the search term
                  and either the formatted product texts or an error message.
        """
        products = api_data.get("products", [])
        if not products:
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            # --- Extract Simple String Fields with fallbacks ---
            prod_id = product.get('prod_id', 'N/A').strip() or 'N/A'
            title = product.get('title', 'N/A').strip() or 'N/A'
            desc = product.get('description', 'N/A').strip() or 'N/A'
            gender = product.get('gender', 'N/A').strip() or 'N/A'
            age_group = product.get('age_group', 'N/A').strip() or 'N/A'
            fit = product.get('fit', 'N/A').strip() or 'N/A'
            category = product.get('category', 'N/A').strip() or 'N/A'
            inseam = product.get('inseam', 'N/A').strip() or 'N/A'
            material = product.get('material', 'N/A').strip() or 'N/A'

            # --- CORRECTED: Extract and Format variant colors FOR EACH PRODUCT ---
            # This logic is now inside the loop, just like in your JcrewParser.
            all_variant_colors_list = product.get("ALL_VARIANT_COLORS", [])
            all_colors_formatted = "/".join(all_variant_colors_list) if all_variant_colors_list else 'N/A'

            # --- Extract and Format Other List Fields ---
            features_list = product.get('features', [])
            features = ", ".join(features_list) if features_list else 'N/A'

            activity_list = product.get('activity', [])
            activity = ", ".join(activity_list) if activity_list else 'N/A'
            
            seasons_list = product.get('seasons', [])
            seasons = ", ".join(seasons_list) if seasons_list else 'N/A'

            # --- Assemble the formatted string for the LLM ---
            llm_texts.append(f"""prod {i + 1}:
prod_id: {prod_id}
title: {title}
description: {desc}
gender: {gender}
age_group: {age_group}
color: {all_colors_formatted}
fit: {fit}
category: {category}
inseam: {inseam}
features: {features}
activity: {activity}
material: {material}
seasons: {seasons}
""")
            
        return self._format_llm_output(search_keyword, llm_texts)