import os
from datetime import datetime


class Obsidian:
    def __init__(self, date:datetime):
        self.date = date
        if 'OBSIDIAN_VAULT_PATH' not in os.environ:
            print('OBSIDIAN_VAULT_PATH is not set. Please set it and try again.')
            exit(1)
        self.obsidian_vault_path = os.getenv('OBSIDIAN_VAULT_PATH')
        self.obsidian_path = os.getenv('OBSIDIAN_PATH', '%Y/%m-%B/%Y-%m-%d Browsing.md')

    def save_to_obsidian(self, markdown_content):
        full_path = os.path.join(self.obsidian_vault_path, self.date.strftime(self.obsidian_path))
        # ensure the path exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'w') as md_file:
            md_file.write(markdown_content)

        print(f"Saved summaries to {full_path}")
