import asyncio
import json
import os

from reading_history.firefox import read_history
from reading_history.llm.open_ai import OpenAIGPT
from reading_history.obsidian import Obsidian
from reading_history.run_config import RunConfig, RunCache
from reading_history.url_sorter import UrlSorter
from reading_history.web_page_fetcher import WebPageFetcher


async def process_ai_responses(directory, fetcher, file_extension):
    refined_results = []
    for file in os.listdir(directory):
        if not os.path.splitext(file)[1] == file_extension:
            continue
        with open(os.path.join(directory, file), 'r') as f:
            try:
                json_data = json.load(f)
                for article in json_data['results']:
                    if article['educational']:
                        print('Getting content for {}'.format(article['url']))
                        try:
                            content = fetcher.get_article(article['url'])
                            if not content:
                                continue
                            refined_results.append(
                                f"URL: {article['url']}, Title: {article['url']}, Description: {content.maintext}\n")
                        except ValueError:
                            continue
            except json.JSONDecodeError:
                print("Failed to decode JSON")

    return refined_results


async def run():
    print('Getting the firefox history...')
    ai = OpenAIGPT()
    fetcher = WebPageFetcher()
    url_sorter = UrlSorter()

    entries = list(filter(url_sorter.is_valid_callback, read_history()))
    print('There are {} entries'.format(len(entries)))

    website_data = await fetcher.get_website_data(entries)
    website_chunks = ai.chunk_data_based_on_tokens(website_data)
    print('Processing {} chunks'.format(len(website_chunks)))
    await asyncio.gather(*[ai.evaluate_educational_value(chunk) for chunk in website_chunks])

    results_dir = RunCache().educational_cache
    refined_results = await process_ai_responses(results_dir, fetcher, '.json')

    refined_chunks = ai.chunk_data_based_on_tokens(refined_results)
    print('Processing {} chunks'.format(len(refined_chunks)))
    await asyncio.gather(*[ai.summarize_articles(chunk) for chunk in refined_chunks])

    summaries_dir = RunCache().summaries_cache
    markdown_content = ''
    for file in os.listdir(summaries_dir):
        if not os.path.splitext(file)[1] == '.md':
            continue
        with open(os.path.join(summaries_dir, file), 'r') as f:
            markdown_content += f.read() + '\n'

    obsidian = Obsidian()
    obsidian.save_to_obsidian(markdown_content)
