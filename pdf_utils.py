import pdfplumber
from cachetools import cached, TTLCache
from io import BytesIO
import tiktoken
import re

cache = TTLCache(maxsize=100, ttl=86400)


def split_into_many(text: str, max_tokens: int) -> list[str]:
    tokenizer = tiktoken.get_encoding("cl100k_base")
    sentences = text.split('. ')

    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]

    chunks = []
    tokens_so_far = 0
    chunk = []

    # Loop through the sentences and tokens joined together in a tuple
    for sentence, token in zip(sentences, n_tokens):

        # If the number of tokens so far plus the number of tokens in the current sentence is greater
        # than the max number of tokens, then add the chunk to the list of chunks and reset
        # the chunk and tokens so far
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")
            chunk = []
            tokens_so_far = 0

        # If the number of tokens in the current sentence is greater than the max number of
        # tokens, go to the next sentence
        if token > max_tokens:
            continue

        # Otherwise, add the sentence to the chunk and add the number of tokens to the total
        chunk.append(sentence)
        tokens_so_far += token + 1

    return chunks


def remove_blankspaces_and_newlines(text_pages: list[str]) -> str:
    context = " ".join(text_pages)
    context = context.replace("\n", " ")
    context = context.strip()
    if context != '':
        return context


def clean_split_process(text_pages: list[str], max_tokens: int) -> list[dict]:
    context = " <page> ".join(text_pages)
    context = context.replace("\n", " ")
    context = context.strip()

    texts = split_into_many(context, max_tokens)
    page = 0
    index = 0
    resulting_docs = list()
    for text in texts:
        resulting_docs.append({"source": str(index), "text": text.replace("<page>", "").strip(), "page": page})
        index += 1
        page += len(re.findall("<page>", text))
    
    return resulting_docs


@cached(cache)
def text_extraction(file: BytesIO) -> list:
    """
    Parameters
    :pdf_path - path to the pdf file to convert into text
    ------------------------------------------
    Extract and save pad pages in a temp directory
    """
    pdf = pdfplumber.open(file)

    text_pages = []
    for _, page in enumerate(pdf.pages):
        single_page_text = page.extract_text()
        text_pages.append(single_page_text)

    return text_pages
