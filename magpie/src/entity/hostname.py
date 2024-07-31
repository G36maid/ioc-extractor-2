import tldextract
from . import domain
from pyparsing import Combine, OneOrMore

# parser
def verify_hostname(string, loc, tokens):

    # tokens is pyparsing.ParseResults
    extraction = tldextract.extract(tokens[0])
    verification = tokens[0] == "{}.{}.{}".format(
        extraction.subdomain, extraction.domain, extraction.suffix
    )
    return verification


expr = Combine(
    domain.prefix + OneOrMore("." + domain.expr | "." + domain.prefix)
).addCondition(verify_hostname)

parser = expr.setResultsName("Hostname")
