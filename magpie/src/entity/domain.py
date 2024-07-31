import requests
import tldextract
from functools import lru_cache
from functional import seq
# from funcy import seqs
from pyparsing import Combine, Word, alphanums, oneOf, OneOrMore, ZeroOrMore


class TopLevelDomain(object):

    # iana tlds
    URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
    MD5 = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt.md5"

    def __init__(self):
        self.tlds = self.get_tlds(self.URL)

    @staticmethod
    def get_tlds(url):
        resp = requests.get(url)
        return resp.text

    @property
    @lru_cache()
    def registed_domains(self):
        
        # merge all domains
        regular_domains = self.tlds.lower().splitlines()

        # add special domains (https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains)
        special_use_domains = [
            "example",
            "invalid",
            "local",
            "localhost",
            "onion",
            "test",
        ]
        crypto_use_domains = ["eth", "zil", "crypto", "bit"]

        domains = (
            seq(regular_domains + special_use_domains + crypto_use_domains)
            .drop(1)
            .filter_not(lambda tld: tld.startswith("xn--"))
            .sorted()
            .cache()
        )

        return domains.to_list()


# parser
# load and update tlds
tlds = TopLevelDomain()
tlds_to_text = " ".join(tlds.registed_domains)


# make expr
def verify_domain(string, loc, tokens):
    # tokens is pyparsing.ParseResults
    token = tokens[0].replace("[.]", ".")
    extraction = tldextract.extract(token)
    verification = token == "{}.{}".format(extraction.domain, extraction.suffix)
    return verification


top_level_domain = OneOrMore(oneOf(["[.]", "."]) + oneOf(tlds_to_text, asKeyword=True))
prefix = Word(alphanums.lower() + "-", excludeChars="/")
expr = Combine(
    prefix
    + ZeroOrMore(oneOf(["[.]", "."]) + prefix, stopOn=top_level_domain)
    + top_level_domain
).addCondition(verify_domain)

parser = expr.setResultsName("Domain")
