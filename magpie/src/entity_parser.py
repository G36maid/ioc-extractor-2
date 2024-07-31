import spacy
from spacy.symbols import ORTH
from functional import seq
from ..src.html_analyzer import Analyzer
from ..src.entity import (
    attack_technique,
    bitcoin_address,
    cve,
    defender_threat,
    domain,
    email,
    filehash_md5,
    filehash_sha1,
    filehash_sha256,
    filepath,
    hostname,
    ipv4,
    ipv6,
    # keyword,
    sslcert_fingerprint,
    uri,
    url,
)

class Parser(object):

    def __init__(self) -> None:
        self.parser = self.construct_parser()

    def construct_parser(self):
        parser = (
            defender_threat.parser
            | uri.parser
            | url.parser
            | email.parser
            | hostname.parser
            | domain.parser
            | sslcert_fingerprint.parser
            | ipv6.parser
            | ipv4.parser
            | cve.parser
            | attack_technique.parser
            | filepath.parser
            | filehash_sha256.parser  # len = 64
            | filehash_sha1.parser  # len = 40
            | bitcoin_address.parser  # len = 34
            | filehash_md5.parser  # len = 32
            # | keyword.make_parser(self.extracted_keywords)  # generate keywords parser
        )
        return parser
    
    def iterscan(self, content):
        """
        for each scanning result, returns a tuple of:
            - matched tokens (packaged as a ParseResults object)
            - start location of the matched text in the given source string
            - end location in the given source string
        """

        # generator
        scanning = self.parser.scanString(content)
        scan_results = (
            seq(scanning)
            .starmap(lambda result, start, end: (
                result[0].rstrip(Analyzer.remove_words,), result.getName(), (start, end), result.asDict()))
            .cache()
        )

        def func():
            pass
        