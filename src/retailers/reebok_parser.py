from .base_parser import BaseParser

class ReebokParser(BaseParser):
    """
    A parser for processing product data from a Reebok API response.

    This class extracts specific product information (Title, Description, Color,
    Target User, Occasion, and Age) based on the provided JSON payload structure.
    """
    def parse_response(self, search_keyword, api_data):
        """
        Parses the API response to extract and format product data.

        Args:
            search_keyword (str): The original search term used for the API query.
            api_data (dict): The JSON data returned from the API.

        Returns:
            dict: A dictionary formatted for the LLM, containing the search term
                  and either the formatted product texts or an error message.
        """
        # Handle case where api_data might be the list itself or a dict containing 'products'
        if isinstance(api_data, list):
            products = api_data
        else:
            products = api_data.get("products", [])

        if not products:
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            # --- Extract String Fields ---
            title = product.get('title', 'N/A')
            title = title.strip() if title else 'N/A'

            description = product.get('description', 'N/A')
            description = description.strip() if description else 'N/A'

            # --- Extract and Format List Fields ---

            # 1. Color (from ALL_VARIANT_COLORS)
            color_list = product.get("ALL_VARIANT_COLORS", [])
            if isinstance(color_list, list):
                color = "/".join(color_list) if color_list else 'N/A'
            else:
                color = str(color_list) if color_list else 'N/A'

            # 2. Target User (from TARGET_USERS)
            users_list = product.get("TARGET_USERS", [])
            if isinstance(users_list, list):
                target_user = ", ".join(users_list) if users_list else 'N/A'
            else:
                target_user = str(users_list) if users_list else 'N/A'

            # 3. Occasion (from OCCASION)
            occasion_list = product.get("OCCASION", [])
            if isinstance(occasion_list, list):
                occasion = ", ".join(occasion_list) if occasion_list else 'N/A'
            else:
                occasion = str(occasion_list) if occasion_list else 'N/A'

            # 4. Age (from AGE)
            age_list = product.get("AGE", [])
            if isinstance(age_list, list):
                age = ", ".join(age_list) if age_list else 'N/A'
            else:
                age = str(age_list) if age_list else 'N/A'


            # --- Assemble the formatted string for the LLM ---
            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {description}
color: {color}
target user: {target_user}
occasion: {occasion}
age: {age}
""")

        return self._format_llm_output(search_keyword, llm_texts)