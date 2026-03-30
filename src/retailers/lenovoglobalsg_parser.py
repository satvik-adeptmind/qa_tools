from .base_parser import BaseParser

class LenovoGlobalSgParser(BaseParser):
    def parse_response(self, search_keyword, api_data):
        products = api_data.get("products", [])
        if not products:
            return {"search_term": search_keyword, "error": "No products returned."}

        llm_texts = []
        for i, product in enumerate(products):
            title = product.get('title', 'N/A').strip()
            description = product.get('description', 'N/A').strip()
            processor = product.get('processor', 'N/A').strip()
            operatingsystem = product.get('operatingsystem', 'N/A').strip()
            display = product.get('display', 'N/A').strip()
            graphics = product.get('graphics', 'N/A').strip()
            memory = product.get('memory', 'N/A').strip()
            harddrive = product.get('harddrive', 'N/A').strip()

            details_text = f"""description: {description}
processor: {processor}
operatingsystem: {operatingsystem}
display: {display}
graphics: {graphics}
memory: {memory}
harddrive: {harddrive}"""

            llm_texts.append(f"""prod {i + 1}:
title: {title}
{details_text}""")

        return self._format_llm_output(search_keyword, llm_texts)