from .base_parser import BaseParser

class DicksSportingGoodsParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        # Extract products from the payload
        products = api_data.get("products",[])
        if not products: 
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts =[]
        for i, product in enumerate(products):
            # Extract standard fields
            title = str(product.get('title', 'N/A')).strip() or 'N/A'
            desc = str(product.get('description', 'N/A')).strip() or 'N/A'
            
            # Extract, filter, and format additional_fields
            add_fields_list = product.get('additional_fields',[])
            if isinstance(add_fields_list, list) and add_fields_list:
                # Filter out elements that start with 'topologies:' or 'category:'
                filtered_fields =[
                    str(field) for field in add_fields_list 
                    if isinstance(field, str) 
                    and not field.startswith("topologies:") 
                    and not field.startswith("category:")
                ]
                
                # Join the remaining fields if the list isn't empty after filtering
                if filtered_fields:
                    additional_fields = " | ".join(filtered_fields)
                else:
                    additional_fields = 'N/A'
            else:
                additional_fields = 'N/A'
        
            # Construct the formatted string for the LLM
            llm_texts.append(f"""prod {i + 1}:
title: {title}
description: {desc}
additional_fields: {additional_fields}
""")
            
        return self._format_llm_output(search_keyword, llm_texts)
