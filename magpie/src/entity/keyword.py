from typing import List
from gensim.summarization.keywords import keywords
from pyparsing import oneOf


def make_parser(keywords: List[str]):
    keywords_to_text = " ".join(keywords)
    expr = oneOf(keywords_to_text, caseless=True, asKeyword=True)
    return expr.setResultsName("Keyword")
