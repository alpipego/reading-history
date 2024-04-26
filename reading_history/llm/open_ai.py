import inspect
import os

from openai import AsyncOpenAI

from reading_history.llm.ai_interface import AIInterface


class OpenAIGPT(AIInterface):
    def __init__(self):
        super().__init__()
        self.client = AsyncOpenAI(
            organization=os.getenv('OPENAI_API_ORG', None),
            project=os.getenv('OPENAI_API_PROJECT', None)
        )
        self.model_name = os.getenv('OPENAI_API_MODEL', 'gpt-4-turbo')

    async def evaluate_educational_value(self, data):
        print('Sending articles to OpenAI API for evaluation')
        filename = inspect.currentframe().f_code.co_name
        response = await self._send_request(filename, data)

        self._dump_educational_decision(response.choices[0].message.content)

    async def summarize_articles(self, data):
        print('Sending articles for summarization to OpenAI API')
        filename = inspect.currentframe().f_code.co_name
        response = await self._send_request(filename, data)

        self._dump_summaries(response.choices[0].message.content)

    async def _send_request(self, filename: str, data: list):
        with open(os.path.join(self.prompts_dir, f"{filename}.txt"), 'r') as f:
            system_prompt = f.read()

        messages = [{
            "role": "system",
            "content": system_prompt
        }, {
            'role': 'user',
            'content': '\n'.join(data)
        }]

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )

        return response
