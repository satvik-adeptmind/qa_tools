from .base_parser import BaseParser

class PetSuperMarketParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            title = product.get('title', 'N/A').strip() or 'N/A'
            desc = product.get('description', 'N/A').strip() or 'N/A'
            pet_category = product.get('pet_category', 'N/A').strip() or 'N/A'
            pet_type = product.get('pet_type', 'N/A').strip() or 'N/A'
            pet_life_stage = product.get('pet_life_stage', 'N/A').strip() or 'N/A'
            pet_flavor = product.get('pet_flavor', 'N/A').strip() or 'N/A'
            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {desc}
pet_category: {pet_category}
pet_type: {pet_type}
pet_life_stage: {pet_life_stage}
pet_flavor: {pet_flavor}""")
        return self._format_llm_output(search_keyword, llm_texts)