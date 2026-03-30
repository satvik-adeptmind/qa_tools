from .base_parser import BaseParser

class PacsunParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products:
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            title = product.get('title', 'N/A')
            description = product.get('description', 'N/A')

            gender = 'N/A'
            age = 'N/A'
            color = 'N/A'
            pattern = 'N/A'
            sleeve_type = []
            neckline = []
            fabric = []

            models = product.get('models', [])
            if models and models[0].get('variants'):
                first_variant = models[0]['variants'][0]
                gender = first_variant.get('gender', 'N/A')
                age = first_variant.get('age', 'N/A')
                color = first_variant.get('color', 'N/A')
                pattern = first_variant.get('pattern', 'N/A')

            cu_attributes = product.get('cu_attributes', {})
            sleeve_type = cu_attributes.get('SLEEVE_TYPE', [])
            neckline = cu_attributes.get('NECKLINE', [])
            fabric = cu_attributes.get('FABRIC', [])

            def format_list_to_str(lst):
                return ", ".join(lst) if lst else 'N/A'

            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {description}
gender: {gender}
age: {age}
color: {color}
pattern: {pattern}
SLEEVE_TYPE: {format_list_to_str(sleeve_type)}
NECKLINE: {format_list_to_str(neckline)}
FABRIC: {format_list_to_str(fabric)}""")

        return self._format_llm_output(search_keyword, llm_texts)