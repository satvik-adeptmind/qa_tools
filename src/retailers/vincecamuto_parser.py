from .base_parser import BaseParser

class VinceCamutoParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            prod_id = product.get('prod_id', 'N/A').strip() or 'N/A'
            title = product.get('title', 'N/A').strip() or 'N/A'
            desc = product.get('description', 'N/A').strip() or 'N/A'
            image = product.get('image', 'N/A').strip() or 'N/A'
        
            llm_texts.append(f"""prod {i + 1}:
prod_id: {prod_id}
title: {title}
description: {desc}
image: {image}
""")
        return self._format_llm_output(search_keyword, llm_texts)