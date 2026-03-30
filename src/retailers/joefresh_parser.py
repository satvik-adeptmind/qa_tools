from .base_parser import BaseParser

class JoeFreshParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: 
            return {"search_term": search_keyword, "error": "No products returned."}
        
        llm_texts = []
        # Define the additional keys to be extracted from the product payload.
        ATTRIBUTES_TO_EXTRACT = ["SEASON", "OCCASION", "VIBE", "LOOK"]

        for i, product in enumerate(products):
            title = product.get('title', 'N/A').strip() or 'N/A'
            desc = product.get('description', 'N/A').strip() or 'N/A'
            
            # Start building the formatted lines for the LLM output.
            lines = [f"prod {i + 1}:", f"title: {title}", f"description: {desc}"]

            # Handle color extraction and formatting separately.
            all_colors = product.get("ALL_VARIANT_COLORS", [])
            if all_colors:
                # Format colors into the "light brown/navy" format.
                colors_str = "/".join([c.lower() for c in all_colors])
                lines.append(f"color: {colors_str}")

            # Loop through the other defined attributes and extract them.
            for key in ATTRIBUTES_TO_EXTRACT:
                if values := product.get(key):
                    # Convert the key to lowercase for display (e.g., "SEASON" -> "season").
                    display_key = key.lower()
                    # Join the list of values into a single comma-separated string.
                    str_values = ", ".join(values)
                    lines.append(f"{display_key}: {str_values}")
            
            llm_texts.append("\n".join(lines))
            
        return self._format_llm_output(search_keyword, llm_texts)