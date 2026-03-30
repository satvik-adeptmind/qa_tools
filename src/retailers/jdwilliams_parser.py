from .base_parser import BaseParser

class JDWilliamsParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: return {"search_term": search_keyword, "error": "No products returned."}
        
        llm_texts = []
        fields = self.config['parser_settings']['fields_to_extract']
        for i, product in enumerate(products):
            details = [f"{f}: {v}" for f in fields if (v := product.get(f))]
            if details:
                llm_texts.append(f"prod {i + 1}:\n" + "\n".join(details))
        return self._format_llm_output(search_keyword, llm_texts)