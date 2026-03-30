from .base_parser import BaseParser

class UniqueVintageParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            title = product.get('title', 'N/A').strip() or 'N/A'
            desc = product.get('description', 'N/A').strip() or 'N/A'

            # Extract color and size from the first variant of the first model
            color = 'N/A'
            size = 'N/A'
            models = product.get('models')
            if models and isinstance(models, list) and len(models) > 0:
                first_model = models[0]
                if first_model and isinstance(first_model, dict):
                    color = first_model.get('color', 'N/A')
                    variants = first_model.get('variants')
                    if variants and isinstance(variants, list) and len(variants) > 0:
                        first_variant = variants[0]
                        if first_variant and isinstance(first_variant, dict):
                            # Look for size in selectedOptions
                            selected_options = first_variant.get('selectedOptions')
                            if selected_options and isinstance(selected_options, list) and len(selected_options) > 0:
                                for option in selected_options:
                                    if option and isinstance(option, dict) and option.get('name', '').lower() == 'size':
                                        size = option.get('value', 'N/A')
                                        break

            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {desc}
color: {color}
size: {size}""")
        return self._format_llm_output(search_keyword, llm_texts)
