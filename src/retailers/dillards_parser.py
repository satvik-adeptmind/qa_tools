from .base_parser import BaseParser

class DillardsParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: 
            return {"search_term": search_keyword, "error": "No products returned."}
        
        llm_texts = []
        for i, product in enumerate(products):
            details = []
            
            def add(key, val):
                # Ensure the value is not empty or None before adding
                if val: 
                    # If the value is a list, join its elements with a comma
                    if isinstance(val, list):
                        val = ", ".join(map(str, val))
                    # Check again after joining, in case the list was empty or contained empty strings
                    if val:
                        details.append(f"{key}: {val}")
            
            # Add basic product attributes
            add("title", product.get("title"))
            add("description", product.get("description"))
            
            # Process all additional fields
            additional_fields = product.get("additional_fields", [])
            for field in additional_fields:
                if ":" in field:
                    # Split the string at the first colon to separate key and value
                    key, value = field.split(":", 1)
                    add(key.strip(), value.strip())
            
            if details:
                llm_texts.append(f"prod {i + 1}:\n" + "\n".join(details))
                
        return self._format_llm_output(search_keyword, llm_texts)