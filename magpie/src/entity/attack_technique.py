from pyparsing import Combine, Optional, Literal, Word, nums

expr = Combine(
    Literal("T1") + Word(nums, exact=3) + Optional(".0" + Word(nums, exact=2))
)
parser = expr.setResultsName("Attack Techniques")