from .base_parser import BaseParser

class LenovoLasParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: return {"search_term": search_keyword, "error": "No products returned."}
        
        llm_texts = []
        fields = self.config['parser_settings']['fields_to_extract']
        for i, product in enumerate(products):
            details = []
            for field in fields:
                value = product.get(field, 'N/A')
                if not value or (isinstance(value, str) and not value.strip()):
                    value = 'N/A'
                details.append(f"{field}: {value}")
            
            llm_texts.append(f"prod {i + 1}:\n" + "\n".join(details))
        return self._format_llm_output(search_keyword, llm_texts)