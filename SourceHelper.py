from pdf_utils import text_extraction, remove_blankspaces_and_newlines, clean_split_process
from web_utils import get_subpages
from llm_utils import LanguageModel
from dotenv import load_dotenv
from io import BytesIO
import pandas as pd
import langdetect
import os


class Source:
    def __init__(self, env_file: str = ".env"):
        load_dotenv(env_file)
        self.llm = LanguageModel(os.getenv("API_KEY"), os.getenv("ORG_ID"))  # Load Model
        self.source_name = ""
        self.text = ""
        self.texts = list()
        self.lang = "en"

    def reset_state(self, env_file: str = ".env"):
        load_dotenv(env_file)
        self.llm = LanguageModel(os.getenv("API_KEY"), os.getenv("ORG_ID"))  # Load Model

    def current_expense(self):
        return self.llm.get_usages(pd.read_csv(os.getenv("PRICE_PATH")))


class DocumentHelper(Source):
    def __init__(self, env_file: str = ".env"):
        super().__init__(env_file)
        self.conversation = list()
        self.pages = list()

    def load_file(self, document: BytesIO, document_name: str = ""):
        self.pages = text_extraction(document)
        self.source_name = document_name
        self.text = remove_blankspaces_and_newlines(self.pages)
        self.lang = langdetect.detect(remove_blankspaces_and_newlines(self.pages))
        texts = clean_split_process(self.pages, int(os.getenv("MAX_TOKENS")))
        texts = [dict(i, **{"document": self.source_name}) for i in texts]
        self.texts = self.llm.batch_embeddings(texts, os.getenv("EMBEDDING_MODEL"))


class WebHelper(Source):
    def __init__(self, env_file: str = ".env"):
        super().__init__(env_file)
        self.conversation = list()
        self.pages = dict()

    def load_web(self, url: str, document_name: str = ""):
        self.pages = get_subpages(url)
        self.source_name = document_name
        for page_url, page in self.pages.items():
            text = remove_blankspaces_and_newlines([page])
            self.text += "\n" + str(text)
            texts = clean_split_process([text], int(os.getenv("MAX_TOKENS")))
            texts = [dict(i, **{"document": page_url}) for i in texts]
            self.texts = self.llm.batch_embeddings(texts, os.getenv("EMBEDDING_MODEL"))
        self.lang = langdetect.detect(self.text)

