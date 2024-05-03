# Import your Firefox History into Obsidian

This project aims to generate a _reading history_ or _reference work_ for articles read during a day and. 
It does this by reading the firefox history, removes unwanted items (like search engine results pages) by filtering them.
This filtered list of URLs is then interpreted by an LLM to decide whether there is educational value.
These articles that provide long-term value are then send "in full"&mdash;depending on the model's context&mdash; back to the LLM to be summarized and tagged. These summaries are in turn saved to an Obsidian note.

Every run has an id and gets cached into the `cache` directory. The raw HTML for articles, is cached into `cache/documents`. Caches will be purged at the end of a run after seven days.

## Configuration

Here are the environment variables that you can set in your `.env` file for this project. See the provided `.env.sample` file. 

<dl>
<dt>OPENAI_API_KEY</dt> <dd>The API key provided to you by the OpenAI platform. This is a required variable and the program won't work if it's not set.</dd>
<dt>OPENAI_API_MODEL</dt> <dd>The specific OpenAI model to use. If this variable isn't set, the program will default to using the 'gpt-4-turbo' model.</dd>
<dt>OPENAI_API_ORG</dt> <dd>The OpenAI organization. This variable is optional. If it's not set, the default value will remain empty.</dd>
<dt>OPENAI_API_PROJECT</dt> <dd>The specific project in your OpenAI workspace. This variable is optional as well. If it's not set, the default value will remain empty.</dd>
<dt>AI_API_MAX_TOKENS</dt> <dd>The maximum number of tokens that a request can hold. If this variable isn't set, the program will limit the request to hold up to 100000 tokens. You might need to adjust this value based on the specific model you've chosen.</dd>
<dt>FIREFOX_PROFILE_DIR</dt> <dd>The absolute system path to your Firefox profile. This variable is required and the program won't work if it's not set.</dd>
<dt>OBSIDIAN_VAULT_PATH</dt> <dd>The absolute system path to your Obsidian vault. Like the Firefox profile path, this is also a required variable.</dd>
<dt>OBSIDIAN_PATH</dt> <dd>The specific path inside Obsidian. If not set, it defaults to representing the current date in the %Y/%m-%B/%Y-%m-%d Browsing.md format: year/month-month name/date Browsing.md.</dd>
</dl>

### Flags

* `--date=<str>` If you want to get the history for another day, pass a `date` flag to the program. It's capable of handling different absolute and relative date formats; e.g., `2024-04-30` or `yesterday`.
    
    `python main.py --date=yesterday`

### URL Filters

Currently, URL filters will only be applied with a simple `url.startswith(<string>)` check.

See `config/search_engines.txt` for a list of search engine URLs that will be filtered.

You can add a file `config/blocklist.txt` to filter additional URLs. I have add the URL to my website https://www.alexandergoller.com, and some random URLs that I know I don't ever want to see in my summary, like https://twitter.com/home. or my GitHub URL https://github.com/alpipego. 

**Note** this will remove the twitter home/stream page, but not individual tweets. Since the crawler can't log in or interpret JavaScript, twitter.com URLs won't ever show up in the results anyway. ¯\_(ツ)_/¯

## Roadmap

* Add Claude-3 models
* Add self-hosted Lama3 models
* Fetch URLs asynchronously

Feel free to contribute to this project by reporting bugs or fixing other issues. Pull-Requests are welcome.