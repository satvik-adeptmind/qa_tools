from .base_parser import BaseParser

class DavidJonesParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            title = product.get('title', 'N/A').strip() or 'N/A'
            desc = product.get('description', 'N/A').strip() or 'N/A'
            color = product.get('color', 'N/A').strip() or 'N/A'
        
            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {desc}
color: {color}""")
        return self._format_llm_output(search_keyword, llm_texts)