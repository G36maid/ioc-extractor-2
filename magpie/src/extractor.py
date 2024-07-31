import html, re

from lxml import etree
from collections import namedtuple
from functional import seq


class ContentExtractor:
    # extract readable content from html element
    Content = namedtuple("Content", ["property", "text", "span"])

    def __init__(self) -> None:
        pass

    @staticmethod
    def sequential_search(patterns, string):
        SearchingResult = namedtuple("SearchingResult", ["group", "span"])
        last_index = 0
        for pattern in list(patterns):

            try:
                # search with re.search, correct span index with previous one
                searching = pattern.search(string[last_index:])
                span_correction = tuple(
                    last_index + index for index in searching.span()
                )
                # update last span index for next match, then return new correct span
                last_index = searching.end()
                yield SearchingResult(searching.group(), span_correction)

            except:
                pass  # avoid to non-existed pattern

    @staticmethod
    def get_contents(element: etree._Element):
        # make searching patterns
        def iter_parsers(element):
            RegexParser = namedtuple("RegexParser", ["prop", "expr"])

            for prop in ("text", "tail"):

                if element.__getattribute__(prop) == None:
                    # "element.text" or "element.tail" may not contain string
                    pass

                else:
                    # get text or tail from element, and make regex
                    string = element.__getattribute__(prop)
                    pattern = re.escape(string)
                    yield RegexParser(prop, re.compile(pattern))

        # get searching expression and prop from parser
        parsers = tuple(iter_parsers(element))
        props = map(lambda parser: parser.prop, parsers)
        exprs = map(lambda parser: parser.expr, parsers)

        # take html line of element
        element_html = etree.tounicode(element)
        element_html = html.unescape(element_html)

        # zip parsing results
        parsing_results = ContentExtractor.sequential_search(exprs, element_html)
        aggregations = zip(props, parsing_results)

        # re-format parsing result and element attributes with namedtuple
        contents = (
            seq(aggregations)
            .starmap(
                lambda prop, result: ContentExtractor.Content(
                    property=prop,
                    text=result.group,
                    span=result.span,
                )
            )
            .cache()
        )

        return list(contents)
