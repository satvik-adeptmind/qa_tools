from .base_parser import BaseParser

class BrooksBrothersParser(BaseParser):
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
                    # If the value is a list, join its elements
                    if isinstance(val, list):
                        val = ", ".join(map(str, val))
                    if val: # Check again after joining, in case the list was empty
                        details.append(f"{key}: {val}")
            
            # Add basic product attributes
            add("title", product.get("title"))
            add("description", product.get("description"))
            add("gender", product.get("gender"))
            add("color", product.get("color")) # This gets color from the main product object
            
            # Add material, prioritizing FABRIC from cu_attributes
            add("material", product.get("material")) # Get material from product object first
            
            # Extract fit information from models
            fit = product.get('models', [{}])[0].get('variants', [{}])[0].get("fit")
            add("fit", fit)

            # Add all cu_attributes fields
            attrs = product.get("cu_attributes", {})
            for attr_key, attr_value in attrs.items():
                add(attr_key.lower(), attr_value) # Convert key to lowercase for consistency
            
            if details:
                llm_texts.append(f"prod {i + 1}:\n" + "\n".join(details))
        return self._format_llm_output(search_keyword, llm_texts)