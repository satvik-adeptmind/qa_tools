from .base_parser import BaseParser

class LenovoParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: return {"search_term": search_keyword, "error": "No products returned."}
        
        llm_texts = []
        for i, product in enumerate(products):
            title = product.get('title', 'N/A').strip() or 'N/A'
            details_text = "description: N/A" # Default
            
            if specs := product.get('system_specs'):
                details_text = "system_specs:\n" + "\n".join(f"- {s}" for s in specs)
            elif specs := product.get('tech_spec'):
                details_text = "tech_spec:\n" + "\n".join(f"- {s}" for s in specs)
            elif desc := product.get('description', '').strip():
                details_text = f"description: {desc}"
            
            llm_texts.append(f"""prod {i + 1}:
title: {title}
{details_text}""")
        return self._format_llm_output(search_keyword, llm_texts)