from .base_parser import BaseParser

class BillabongParser(BaseParser):
    """
    A parser for processing product data from a Billabong API response.

    This class extracts specific product information (title, description, color,
    FABRIC, CLOSURE, NECKLINE, OCCASION, and TARGET_USERS) based on the
    provided JSON payload structure.
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

            # 1. Color (Mapped from ALL_VARIANT_COLORS)
            # Expected payload: "ALL_VARIANT_COLORS": ["CHARCOAL HEATHER"]
            color_list = product.get("ALL_VARIANT_COLORS", [])
            # Ensure it is a list before joining
            if isinstance(color_list, list):
                color = "/".join(color_list) if color_list else 'N/A'
            else:
                color = str(color_list) if color_list else 'N/A'

            # 2. Fabric (Mapped from FABRIC)
            # Expected payload: "FABRIC": ["SILK"]
            fabric_list = product.get("FABRIC", [])
            if isinstance(fabric_list, list):
                fabric = ", ".join(fabric_list) if fabric_list else 'N/A'
            else:
                fabric = str(fabric_list) if fabric_list else 'N/A'

            # 3. Closure (Mapped from CLOSURE)
            # Expected payload: "CLOSURE": ["BUTTON"]
            closure_list = product.get("CLOSURE", [])
            if isinstance(closure_list, list):
                closure = ", ".join(closure_list) if closure_list else 'N/A'
            else:
                closure = str(closure_list) if closure_list else 'N/A'

            # 4. Neckline (Mapped from NECKLINE)
            # Expected payload: "NECKLINE": ["COLLARED"]
            neckline_list = product.get("NECKLINE", [])
            if isinstance(neckline_list, list):
                neckline = ", ".join(neckline_list) if neckline_list else 'N/A'
            else:
                neckline = str(neckline_list) if neckline_list else 'N/A'
                
            # 5. Occasion (Mapped from OCCASION)
            # Expected payload: "OCCASION": ["FORMAL", "WEAR_TO_WORK"]
            occasion_list = product.get("OCCASION", [])
            if isinstance(occasion_list, list):
                occasion = ", ".join(occasion_list) if occasion_list else 'N/A'
            else:
                occasion = str(occasion_list) if occasion_list else 'N/A'

            # 6. Target Users (Mapped from TARGET_USERS)
            # Expected payload: "TARGET_USERS": ["UNISEX"]
            users_list = product.get("TARGET_USERS", [])
            if isinstance(users_list, list):
                target_users = ", ".join(users_list) if users_list else 'N/A'
            else:
                target_users = str(users_list) if users_list else 'N/A'

            # --- Assemble the formatted string for the LLM ---
            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {description}
color: {color}
FABRIC: {fabric}
CLOSURE: {closure}
NECKLINE: {neckline}
OCCASION: {occasion}
TARGET_USERS: {target_users}
""")
            
        return self._format_llm_output(search_keyword, llm_texts)