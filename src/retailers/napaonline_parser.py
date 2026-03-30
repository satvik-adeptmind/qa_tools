from .base_parser import BaseParser

class NapaOnlineParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products: return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            details = []
            
            def add_detail(field_name, value):
                if value is None or value == '' or value == []: return
                if field_name == "bullets":
                    formatted = "\n- " + "\n- ".join(map(str, value))
                    details.append(f"{field_name}:{formatted}")
                elif isinstance(value, list):
                    details.append(f"{field_name}: {', '.join(map(str, value))}")
                else:
                    details.append(f"{field_name}: {value}")

            add_detail("title", product.get("title"))
            add_detail("description", product.get("description"))
            add_detail("bullets", product.get("bullets"))
            add_detail("topologies", product.get("topologies"))
            
            universal = product.get("attributes", {}).get("UNIVERSAL")
            if universal: add_detail("universal", universal[0])

            mapping = product.get("vehicle_selector_mapping")
            if mapping: add_detail("model", mapping[0].get("model"))

            if details:
                llm_texts.append(f"prod {i + 1}:\n" + "\n".join(details))
        return self._format_llm_output(search_keyword, llm_texts)