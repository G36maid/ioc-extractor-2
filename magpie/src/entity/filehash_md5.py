"""
from ..util import entropy_threshold
from pyparsing import Word, hexnums

# length of FileHash-MD5, FileHash-IMPHASH, JA3 are all equal to 32
expr = Word(hexnums.lower(), exact=32).addCondition(
    lambda string, loc, tokens: entropy_threshold(
        string, loc, tokens, base=17, threshold=0.8
    )
)

parser = expr.setResultsName("FileHash-MD5")
"""

from pyparsing.core import Regex
parser = Regex(r"\b([a-f0-9]{32}|[A-F0-9]{32})([^a-zA-Z0-9]|$)"
).setResultsName("FileHash-MD5")
