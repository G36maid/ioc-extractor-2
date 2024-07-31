from pyparsing import Combine, Keyword, Word, nums, CaselessKeyword

expr = Combine(Keyword("CVE") + "-" + Word(nums, exact=4) + "-" + Word(nums, min=4))
parser = expr.setResultsName("CVE")