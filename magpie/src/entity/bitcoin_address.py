from src.util import entropy_threshold
from pyparsing import Word, alphanums

expr = Word(alphanums, exact=34).addCondition(
    lambda string, loc, tokens: entropy_threshold(
        string, loc, tokens, base=62, threshold=0.7
    )
)
parser = expr.setResultsName("Bitcoin Address")
