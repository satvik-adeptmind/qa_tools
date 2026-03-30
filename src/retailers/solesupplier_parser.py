from .base_parser import BaseParser

class SoleSupplierParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            title = product.get('title', 'N/A').strip() or 'N/A'
            desc = product.get('description', 'N/A').strip() or 'N/A'
            gender = product.get('gender', 'N/A').strip() or 'N/A'
            
            variants = product.get('models', [{}])[0].get('variants', [])
            colors = {v.get('color') for v in variants if v.get('color')}
            color_str = ", ".join(sorted(list(colors))) if colors else 'N/A'
            
            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {desc}
color: {color_str}
gender: {gender}""")
        return self._format_llm_output(search_keyword, llm_texts)