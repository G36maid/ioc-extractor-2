"""
from ..util import entropy_threshold
from pyparsing import Word, hexnums


expr = Word(hexnums.lower(), exact=64).addCondition(
    lambda string, loc, tokens: entropy_threshold(
        string, loc, tokens, base=17, threshold=0.9
    )
)

parser = expr.setResultsName("FileHash-SHA256")
"""
from pyparsing.core import Regex
parser = Regex(r"\b([a-f0-9]{64}|[A-F0-9]{64})([^a-zA-Z0-9]|$)"
).setResultsName("FileHash-SHA256")
