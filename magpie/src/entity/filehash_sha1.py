"""
from ..util import entropy_threshold
from pyparsing import Word, hexnums

# length of FileHash-SHA1, FileHash-PEHASH are all equal to 40
expr = Word(hexnums.lower(), exact=40).addCondition(
    lambda string, loc, tokens: entropy_threshold(
        string, loc, tokens, base=17, threshold=0.8
    )
)

parser = expr.setResultsName("FileHash-SHA1")
"""

from pyparsing.core import Regex
parser = Regex(r"\b([a-f0-9]{40}|[A-F0-9]{40})([^a-zA-Z0-9]|$)"
).setResultsName("FileHash-SHA1")
