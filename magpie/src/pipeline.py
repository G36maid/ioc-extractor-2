from functional import seq
from itertools import product
from src.analyzer import HTMLElementAnalyzer
from src.extractor import ContentExtractor
from src.parser import EntityParser


analyzer = HTMLElementAnalyzer(document)
extractor = ContentExtractor()
parser = EntityParser(analyzer.keywords)


"""
# same as product_by_contents
lambda element: seq(extractor.get_contents(element)).map(
    lambda content: (element, content)
)
"""


product_by_contents = lambda element: product(
    [element], extractor.get_contents(element)
)

product_by_entities = lambda element, content: product(
    [element], [content], parser.iterscan(content)
)

pipeline_results = (
    seq(analyzer.primary_subtree_leafs)
    .map(product_by_contents)
    .flatten()
    .starmap(product_by_entities)
    .flatten()
    .cache()
)

tokens = pipeline_results.starmap(
    lambda element, content, text: (
        text.string,
        text.entity,
        # element.sourceline,
        element,
        content.property,
        content.span,
        text.span,
    )
)

"""
from lxml import etree

etree.tounicode(analyzer.primary_subtree_leafs[1])[49:108][0:10]
"""