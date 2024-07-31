from pyparsing import Combine, Literal, Word
from pyparsing import alphanums, nestedExpr, originalTextFor

expr = Combine(
    Literal("rule")
    + Word(" ", exact=1)
    + Word(alphanums + "_")
    + Word(" ", exact=1)
    + originalTextFor(
        nestedExpr(
            opener="{",
            closer="}",
        )
    )
)

parser = expr.setResultsName("YARA")