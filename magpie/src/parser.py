from typing import List
from functional import seq
from collections import namedtuple, deque
from more_itertools import pairwise, collapse
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


class EntityParser(object):

    Text = namedtuple("Text", ["entity", "string", "span"])

    def __init__(self, extracted_keywords: List[str] = []) -> None:
        self.extracted_keywords = extracted_keywords
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
        scanning = self.parser.scanString(content.text)
        scan_results = (
            seq(scanning)
            .starmap(lambda token, start, end: ((start, end), token))
            .cache()
        )

        def refill(spans, text=content.text):

            # get head and tail index of content.text
            head, tail = 0, len(content.text)

            # append head and tail index
            indexes = deque(collapse(spans))
            indexes.appendleft(head)
            indexes.append(tail)
            indexes = sorted(set(indexes))

            # bi-grams tokenize indexes
            filled_spans = pairwise(indexes)

            return filled_spans

        # filled with other non-entity spans
        entity_spans = scan_results.starmap(lambda span, token: span).to_list()
        filled_spans = refill(entity_spans, content.text)

        scan_results_dict = scan_results.to_dict()

        # join together
        for span in filled_spans:

            token = scan_results_dict.get(span)

            if token != None:
                entity = token.getName()
                string = token.get(entity)
                yield self.Text(entity, string, span)

            else:
                entity = None
                start, end = span
                string = content.text[start:end]
                yield self.Text(None, string, span)
