from typing import List, Text
import os

class AppInfo:
    """
    General information about the application.

    ***This repo was generated from a cookiecutter template published by myedibleenso and zwellington.
    See https://github.com/clu-ling/clu-template for more info.
    """

    version: Text = "0.1"
    commit: Text = os.environ.get("GIT_COMMIT", "unknown")
    description: Text = "AZX project"

    authors: List[Text] = ['enoriega']
    repo: Text = "https://github.com/clu-ling/clu-azahead"
    license: Text = "MIT License"

    @property
    def download_url(self) -> str:
        return f"{self.repo}/archive/v{self.version}.zip"

info = AppInfo()