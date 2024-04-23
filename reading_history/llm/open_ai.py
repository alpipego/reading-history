import os

from openai import AsyncOpenAI

from reading_history.llm.ai_interface import AIInterface


class OpenAIGPT(AIInterface):
    def __init__(self):
        self.client = AsyncOpenAI(
            organization=os.getenv('OPENAI_API_ORG', None),
            project=os.getenv('OPENAI_API_PROJECT', None)
        )
        self.model_name = os.getenv('OPENAI_API_MODEL', 'gpt-4-turbo')
        self.max_tokens = os.getenv('OPENAI_API_MAX_TOKENS', 4096)

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
            # Example item serialization into prompt text
            item_text = f"URL: {item[0]}, Title: {item[1]}, Description: {item[2]}\nEvaluate: "
            if sum(len(x) for x in current_chunk) + len(item_text) > chunk_size_in_chars:
                chunks.append(current_chunk)
                current_chunk = []
            current_chunk.append(item)

        if current_chunk:  # Add any remaining items as a final chunk
            chunks.append(current_chunk)

        return chunks

    async def analyze(self, data):
        messages = [{
            "role": "system",
            "content": (
                "I will provide you with a list of URLs along with their titles and content. For each URL, "
                "analyze whether the content has educational value. Consider a URL as educational if it "
                "provides useful information, explanations, knowledge, or insights related to academic, "
                "technical, scientific, or practical topics.\n\n"
                "Response Format Guidelines:\n"
                "- If a URL has educational content, start each entry with ## followed by the actual Title\n"
                "  - Then, on the next line, start with '**URL:**', followed by the actual URL.\n"
                "  - On the next line, start with '**Content Summary:**', followed by a concise summary.\n"
                "- If a URL does not have educational content, explain why under the heading '**Explanation:**' "
                "after stating the URL and Title.\n"
                "- Leave a blank line after each URL's response before starting the next entry.\n\n"
                "Here is the list of URLs and their respective titles and content:\n"
            )
        }]

        user_message = ''
        for entry in data:
            url, title, content = entry
            user_message += f"## {title}\n**URL:** {url}\n**Content:** {content}\n\n"

        messages.append({
            "role": "user",
            "content": user_message
        })

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens
        )

        return response.choices[0].message.content
