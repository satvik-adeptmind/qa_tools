from .base_parser import BaseParser

class FootLockerParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        # Foot Locker payloads often wrap products in 'products' or 'entries'
        products = api_data.get("products", [])
        
        if not products: 
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            # Attempt to find name/title
            title = product.get('name') or product.get('title', 'N/A')
            title = title.strip()
            
            desc = product.get('description', 'N/A').strip() or 'N/A'
            
            # Helper to extract list fields and join them into a string
            def _get_list_as_string(key):
                items = product.get(key, [])
                if isinstance(items, list) and items:
                    # Filter out empty strings/None and join
                    return ", ".join(sorted([str(x).strip() for x in items if x]))
                return 'N/A'

            # Extract fields
            gender = _get_list_as_string('GENDER')
            closure = _get_list_as_string('CLOSURE')
            variant_colors = _get_list_as_string('ALL_VARIANT_COLORS')
            season = _get_list_as_string('SEASON')
            occasion = _get_list_as_string('OCCASION')
            vibe = _get_list_as_string('VIBE')
            look = _get_list_as_string('LOOK')
            
            # Format the output block
            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {desc}
gender: {gender}
closure: {closure}
variant_colors: {variant_colors}
season: {season}
occasion: {occasion}
vibe: {vibe}
look: {look}""")
            
        return self._format_llm_output(search_keyword, llm_texts)