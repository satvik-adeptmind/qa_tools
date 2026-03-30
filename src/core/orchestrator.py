import csv
import json
import asyncio
import aiohttp
import math
from tqdm.auto import tqdm

class BatchOrchestrator:
    def __init__(self, config, api_client, data_parser):
        self.config = config
        self.api_client = api_client
        self.data_parser = data_parser
        self.keywords = []

    def _load_keywords(self):
        try:
            path = self.config['input_csv_path']
            with open(path, mode='r', newline='', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                self.keywords = [row[0].strip() for row in reader if row and row[0].strip()]
            if not self.keywords:
                print("No keywords found in the input file.")
                return False
            return True
        except FileNotFoundError:
            print(f"Error: Input file '{path}' not found.")
            return False

    async def _process_keyword(self, session, keyword, progress_bar):
        """Wraps the API call and data parsing for a single keyword."""
        try:
            url, payload = self.data_parser.build_request(keyword)
            api_data = await self.api_client.post(
                session, url,
                headers={'Content-Type': 'application/json'},
                payload=payload,
                timeout=self.config['api_settings']['timeout_seconds']
            )
            result = self.data_parser.parse_response(keyword, api_data)
        except Exception as e:
            max_retries = self.config['retry_settings']['max_retries']
            print(f"All retries failed for '{keyword}'. Final error: {type(e).__name__}")
            result = {"search_term": keyword, "error": f"API/Network Error after {max_retries} attempts: {e}"}
        
        progress_bar.update(1)
        return result

    async def run(self):
        if not self._load_keywords():
            return
        
        total_keywords = len(self.keywords)
        batch_size = self.config['api_settings']['processing_batch_size']
        num_batches = math.ceil(total_keywords / batch_size)
        
        print(f"Found {total_keywords} keywords. Starting processing in {num_batches} batches of up to {batch_size} keywords each.")
        
        all_results = []
        progress_bar = tqdm(total=total_keywords, desc=f"Fetching {self.config['shop_id']} Details")

        async with aiohttp.ClientSession() as session:
            for i in range(num_batches):
                start, end = i * batch_size, (i + 1) * batch_size
                keyword_batch = self.keywords[start:end]

                tasks = [self._process_keyword(session, kw, progress_bar) for kw in keyword_batch]
                batch_results = await asyncio.gather(*tasks)
                all_results.extend(batch_results)
                
                if i < num_batches - 1:
                    sleep_time = self.config['api_settings']['sleep_between_batches']
                    print(f"Batch {i+1}/{num_batches} complete. Pausing for {sleep_time} seconds...")
                    await asyncio.sleep(sleep_time)

        progress_bar.close()
        self._save_results(all_results)
        print("\nProcessing complete.")

    def _save_results(self, results):
        num_files = self.config['num_output_files']
        chunk_size = math.ceil(len(results) / num_files) if num_files > 0 else len(results)
        
        for i in range(num_files):
            start, end = i * chunk_size, (i + 1) * chunk_size
            results_chunk = results[start:end]
            if not results_chunk:
                continue

            # Correctly construct the output path
            output_dir = self.config['output_dir']
            output_path = f"{output_dir}/{self.config['output_filename_base']}_part{i+1}.json"
            
            with open(output_path, 'w', encoding='utf-8') as outfile:
                json.dump(results_chunk, outfile, ensure_ascii=False, indent=4)
            print(f"--> Saved {len(results_chunk)} results to '{output_path}'")

    def _load_keywords(self):
        """Loads keywords either from a file or directly from the orchestrator."""
        if self.keywords:  # Keywords are already provided
            return True

        try:
            path = self.config['input_csv_path']
            with open(path, mode='r', newline='', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                self.keywords = [row[0].strip() for row in reader if row and row[0].strip()]
            if not self.keywords:
                print("No keywords found in the input file.")
                return False
            return True
        except FileNotFoundError:
            print(f"Error: Input file '{path}' not found.")
            return False