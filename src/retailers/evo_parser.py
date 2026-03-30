from .base_parser import BaseParser

class EvoParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: return {"search_term": search_keyword, "error": "No products returned."}
        
        llm_texts = []
        for i, product in enumerate(products):
            title = product.get('title', 'N/A').strip() or 'N/A'
            desc = product.get('description', 'N/A').strip() or 'N/A'
            image_url = product.get('image', 'N/A')
            
            colors = {v.get('color') for m in product.get('models', []) for v in m.get('variants', []) if v.get('color')}
            available_colors = ", ".join(sorted(list(colors))) or "N/A"

            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {desc}
image_url: {image_url}
available_colors: {available_colors}""")
        return self._format_llm_output(search_keyword, llm_texts)