from pyparsing import Combine, NotAny, Word, alphanums, pyparsing_common

# expr = pyparsing_common.ipv6_address
expr = Combine(pyparsing_common.ipv6_address + NotAny(Word(alphanums)))
parser = expr.setResultsName("IPv6")
