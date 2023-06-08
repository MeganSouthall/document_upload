from langchain.schema import Document
from llm_utils import LanguageModel
from dotenv import load_dotenv
from SourceHelper import Source
import itertools
import time
import os


class ChatModel:
    def __init__(self, documents: list[Source], env_file: str = ".env"):
        load_dotenv(env_file)
        self.llm = LanguageModel(os.getenv("API_KEY"), os.getenv("ORG_ID"))
        self.documents = documents
        self.texts = list(itertools.chain.from_iterable([d.texts for d in self.documents]))
        self.conversation = list()

    def reset_state(self, env_file: str = ".env"):
        load_dotenv(env_file)
        self.llm = LanguageModel(os.getenv("API_KEY"), os.getenv("ORG_ID"))  # Load Model
        for doc in self.documents:
            doc.reset_state(env_file)

    def add_document(self, document: Source):
        self.texts.extend(document.texts)

    def chat(self, question: str):
        def __get_meta(el: dict):
            return {"source": el["source"], "page": el["page"], "doc": el["document"]}

        sorted_docs = self.llm.similarity_search(question, self.texts, os.getenv("EMBEDDING_MODEL"))

        mapping = dict()
        book_docs = list()
        i = 0
        for _, el in sorted_docs[:2]:
            mapping[f"s-{i}"] = __get_meta(el)
            book_docs.append(Document(page_content=el['text'], metadata={"source": f"s-{i}"}))

        answer, sources = self.llm.chat(question, book_docs)

        self.conversation.append({"side": "user", "sentence": question, "meta": {
            "source": "",
            "timestamp": time.time()
        }})
        self.conversation.append({"side": "bot", "sentence": answer, "meta": {
            "source": [mapping[s.strip()] if s.strip() in mapping else s.strip() for s in sources],
            "timestamp": time.time()
        }})
