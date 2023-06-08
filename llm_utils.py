from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

from langchain.schema import Document
from operator import itemgetter
from numpy import ndarray
import pandas as pd
import numpy as np
import openai
import re


def vector_similarity(x: list[float], y: list[float]) -> ndarray:
    """
    Returns the similarity between two vectors.

    Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.
    """
    return np.dot(np.array(x), np.array(y))


class LanguageModel:
    def __init__(self, api_key: str, org_id: str):
        openai.api_key = api_key
        openai.organization = org_id
        self.usages = list()
        template = """Given the following extracted parts of a long document and a question, create a final answer with references ("SOURCES"). 
                If you don't know the answer, just say that you don't know. Don't try to make up an answer.
                ALWAYS return a "SOURCES" part in your answer.
                Respond in the same language as the question.

                QUESTION: {question}
                =========
                {summaries}
                =========
                FINAL ANSWER:"""
        self.prompt = PromptTemplate(template=template, input_variables=["summaries", "question"])

    def get_usages(self, pricing):
        df = pd.DataFrame(self.usages, columns=["model", "tokens"])
        df = df.groupby(["model"]).agg("sum").reset_index()
        df = df.merge(pricing, on="model")
        df["total"] = df["tokens"]/1000 * df["price"]
        return df["total"].sum()

    def get_embedding(self, text: str, model: str) -> list[float]:
        result = openai.Embedding.create(
            model=model,
            input=text
        )
        self.usages.append((model, result["usage"]["total_tokens"]))
        return result["data"][0]["embedding"]

    def batch_embeddings(self, df: list[dict], model: str) -> list[dict]:
        def __add_embedding(el: dict, embeddings: list[float]) -> dict:
            el['embedding'] = embeddings
            return el
        return [__add_embedding(e, self.get_embedding(e["text"], model)) for e in df]

    def similarity_search(self, query: str, contexts: list[dict], model: str) -> list[(float, dict)]:
        """
        Find the query embedding and compare it against all of the pre-calculated document embeddings
        to find the most relevant sections.

        Return the list of document sections, sorted by relevance in descending order.
        """
        query_embedding = self.get_embedding(query, model)

        document_similarities = sorted([
            (vector_similarity(query_embedding, doc['embedding']), doc) for doc in contexts
        ], reverse=True, key=itemgetter(0))

        return document_similarities

    def chat(self, question: str, context: list[Document]) -> tuple[str, list]:
        def __split_res(response: str):
            sources_ids = ["source:", "sources:", "fonte:", "fonti:"]
            for sources_id in sources_ids:
                if re.search(sources_id, response, re.IGNORECASE):
                    return re.split(sources_id, response, flags=re.IGNORECASE)
            else:
                return [response]
        chain = load_qa_with_sources_chain(OpenAI(openai_api_key=openai.api_key, temperature=0, max_tokens=512),
                                           chain_type="stuff", prompt=self.prompt)
        raw_response = chain({"input_documents": context, "question": question}, return_only_outputs=True)
        print(raw_response["output_text"])
        res = __split_res(raw_response["output_text"])
        if len(res) == 2:
            text_response = res[0].strip()
            if res[1].endswith("."):
                res[1] = res[1][:-1]
            sources = res[1].split(";") if ";" in res[1] else res[1].split(",")
            sources_clean = list()
            for s in sources:
                sources_clean.extend(s.split("\n"))
            return text_response, sources_clean
        return raw_response["output_text"], []
