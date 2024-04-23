import asyncio

from reading_history.firefox import read_history
from reading_history.llm.open_ai import OpenAIGPT
from reading_history.obsidian import Obsidian
from reading_history.url_sorter import UrlSorter
from reading_history.web_page_fetcher import WebPageFetcher


async def run():
    ai = OpenAIGPT()
    fetcher = WebPageFetcher()
    url_sorter = UrlSorter()
    entries = read_history()
    website_data = []

    for url, title, meta_desc in entries:
        try:
            url = url_sorter.is_valid(url)
            content = fetcher.fetch_and_parse(url)
            if content == '':
                continue
            website_data.append((url, title, content))
        except ValueError:
            pass

    chunks = ai.chunk_data_based_on_tokens(website_data)
    result = await asyncio.gather(*[ai.analyze(chunk) for chunk in chunks])

    obsidian = Obsidian()
    markdown_content = obsidian.results_to_markdown(result)
    obsidian.save_to_obsidian(markdown_content)

    return result
