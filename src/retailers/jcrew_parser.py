from .base_parser import BaseParser

class JcrewParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: 
            return {"search_term": search_keyword, "error": "No products returned."}
        
        llm_texts = []
        LILY_KEYS = self.config['parser_settings']['lily_keys_to_extract']
        
        for i, product in enumerate(products):
            # --- Pinned variant logic remains to get other default attributes ---
            default_image_url = product.get('image')
            all_variants = product.get('models', [{}])[0].get('variants', [])
            
            pinned_variant = None
            if default_image_url and all_variants:
                for v in all_variants:
                    if v.get('image') == default_image_url:
                        pinned_variant = v
                        break

            if not pinned_variant:
                pinned_variant = all_variants[0] if all_variants else {}
            # --- End of pinned variant logic ---

            prod_id = product.get('prod_id', 'N/A') 
            title = product.get('title', 'N/A')
            desc = product.get('description', 'N/A')
            gender = pinned_variant.get('gender', 'N/A')
            
            # **UPDATED**: Get all available colors from the "ALL_VARIANT_COLORS" field.
            all_colors = product.get("ALL_VARIANT_COLORS", [])
            # Format the colors into the "hydrangea/navy/white" format.
            colors_str = "/".join([c.lower() for c in all_colors]) if all_colors else 'N/A'
            
            lines = [f"prod {i + 1}:", f"prod_id: {prod_id}", f"title: {title}", f"description: {desc}", 
                     f"gender: {gender}", f"color: {colors_str}"]

            # Extract Lily AI keys from the pinned variant.
            for key in LILY_KEYS:
                if values := pinned_variant.get(key):
                    display_key = key.replace('lily_', '').replace('_', ' ')
                    str_values = [str(v) for v in values]
                    lines.append(f"{display_key}: {', '.join(str_values)}")
            
            llm_texts.append("\n".join(lines))
            
        return self._format_llm_output(search_keyword, llm_texts)