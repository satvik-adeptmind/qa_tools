from .base_parser import BaseParser

class MadewellParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        # Assuming the API wrapper still returns a dictionary with a "products" list
        products = api_data.get("products", [])
        
        if not products: 
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            # Extract title and description
            title = product.get('title', 'N/A')
            # Ensure title is a string before stripping
            title = title.strip() if isinstance(title, str) else str(title)
            
            desc = product.get('description', 'N/A')
            desc = desc.strip() if isinstance(desc, str) else 'N/A'
            
            # Helper to extract list fields and join them into a string
            def _get_list_as_string(key):
                items = product.get(key, [])
                if isinstance(items, list) and items:
                    # Filter out empty strings/None and join
                    return ", ".join(sorted([str(x).strip() for x in items if x]))
                return 'N/A'

            # Extract fields based on the Madewell JSON structure
            # Note: 'gender' appeared lowercase in your snippet, others were uppercase
            gender = _get_list_as_string('gender')
            variant_colors = _get_list_as_string('ALL_VARIANT_COLORS')
            season = _get_list_as_string('SEASON')
            occasion = _get_list_as_string('OCCASION')
            material = _get_list_as_string('MATERIAL')
            fit_silhouette = _get_list_as_string('FIT&SILHOUETTE')
            heel_type = _get_list_as_string('HEELTYPE')
            vibe = _get_list_as_string('VIBE')
            look = _get_list_as_string('LOOK')
            
            # Format the output block
            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {desc}
gender: {gender}
variant_colors: {variant_colors}
season: {season}
occasion: {occasion}
material: {material}
fit_silhouette: {fit_silhouette}
heel_type: {heel_type}
vibe: {vibe}
look: {look}""")
            
        return self._format_llm_output(search_keyword, llm_texts)