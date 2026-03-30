from .base_parser import BaseParser

class BananaRepublicParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        # Assuming the API returns a list of items under "products" just like the previous parser
        products = api_data.get("products", [])
        if not products: 
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        # list of cu_attributes keys to ignore
        excluded_attrs = {'CATEGORY', 'CARE_INSTRUCTION', 'KEYPHRASE', 'PRICE'}

        for i, product in enumerate(products):
            # 1. Basic Fields
            title = product.get('title', 'N/A') or 'N/A'
            desc = product.get('description', 'N/A') or 'N/A'

            # 2. Colors (from ALL_VARIANT_COLORS)
            # The payload indicates this is a list of strings, e.g., ["White", "Red"]
            colors_list = product.get('ALL_VARIANT_COLORS', [])
            if isinstance(colors_list, list) and colors_list:
                colors = ", ".join(str(c) for c in colors_list)
            else:
                colors = 'N/A'

            # 3. Process cu_attributes
            cu_data = product.get('cu_attributes', {})
            attribute_lines = []

            if cu_data:
                for attr_key, attr_vals in cu_data.items():
                    # Skip excluded attributes
                    if attr_key.upper() in excluded_attrs:
                        continue
                    
                    # Handle value formatting (payload shows values as lists, e.g., ["COTTON"])
                    if isinstance(attr_vals, list):
                        val_str = ", ".join(str(v) for v in attr_vals)
                    else:
                        val_str = str(attr_vals)
                    
                    if val_str:
                        # Convert key to lowercase for cleaner LLM input
                        attribute_lines.append(f"{attr_key.lower()}: {val_str}")

            # 4. Construct the text block
            item_text = f"prod {i + 1}:\n"
            item_text += f"title: {title}\n"
            item_text += f"description: {desc}\n"
            item_text += f"colors: {colors}"
            
            # Append dynamic attributes if they exist
            if attribute_lines:
                item_text += "\n" + "\n".join(attribute_lines)

            llm_texts.append(item_text)

        return self._format_llm_output(search_keyword, llm_texts)