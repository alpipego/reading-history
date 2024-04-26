import json
import os
from hashlib import md5

from reading_history.run_config import RunConfig, RunCache


class AIInterface:
    def __init__(self):
        self.max_tokens = int(os.getenv('AI_API_MAX_TOKENS', 4096))
        self.prompts_dir = 'config/prompts'

    def evaluate_educational_value(self, data):
        raise NotImplementedError("This method needs to be implemented by subclasses.")

    def summarize_articles(self, data):
        raise NotImplementedError("This method needs to be implemented by subclasses.")

    def chunk_data_based_on_tokens(self, data, avg_char_per_token=4, buffer=250):
        """
        Chunk the data into portions that respect the model's max token limit.
        avg_char_per_token is a rough estimation, adjust based on experimentation.
        buffer is to leave space for the model's responses.
        """
        chunk_size_in_chars = ((self.max_tokens - buffer) * avg_char_per_token)  # Convert token limit to char limit
        chunks = []
        current_chunk = []

        for item in data:
            if len(item) > chunk_size_in_chars:  # Check if item_text itself is too long
                item = item[:chunk_size_in_chars]  #

            if sum(len(x) for x in current_chunk) + len(item) > chunk_size_in_chars:
                chunks.append(current_chunk)
                current_chunk = []
            current_chunk.append(item)

        if current_chunk:  # Add any remaining items as a final chunk
            chunks.append(current_chunk)

        return chunks

    @staticmethod
    def _dump_summaries(content: str):
        full_path = os.path.join(RunCache().summaries_cache, md5(content[:500].encode('utf-8')).hexdigest() + '.md')
        with open(full_path, 'w') as markdown_file:
            markdown_file.write(content)

    @staticmethod
    def _dump_educational_decision(content: str):
        json_data = json.loads(content)
        full_path = os.path.join(RunCache().educational_cache, md5(content[:500].encode('utf-8')).hexdigest() + '.json')
        with open(full_path, 'w') as json_file:
            json_file.write(json.dumps(json_data))