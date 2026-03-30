from .base_parser import BaseParser


class SnapOneEnUsParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products:
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            details = []

            def add_detail(field_name, value):
                if value is None or value == "" or value == []:
                    return
                if isinstance(value, list):
                    value = " | ".join(str(v).strip() for v in value if str(v).strip())
                else:
                    value = str(value).strip()
                if value:
                    details.append(f"{field_name}: {value}")

            add_detail("title", product.get("title"))
            add_detail("description", product.get("description"))
            add_detail("features", product.get("features"))

            if details:
                llm_texts.append(f"prod {i + 1}:\n" + "\n".join(details))

        return self._format_llm_output(search_keyword, llm_texts)
