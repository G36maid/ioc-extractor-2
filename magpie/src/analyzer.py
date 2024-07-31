import networkx as nx
from lxml import etree
from functional import seq
from operator import add, mul
from functools import lru_cache
from gensim.summarization import keywords


class HTMLElementAnalyzer(object):
    def __init__(self, doc):
        self.doc = self.is_valid_document(doc)

    def is_valid_document(self, document):
        root = etree.HTML(document)
        if isinstance(root, etree._Element):
            self.root = root
            self.elements = self.root.xpath("//*")
        else:
            raise ValueError("Document is not valid HTML content.")
        return document

    @staticmethod
    def get_printable_elements(elements):

        # check element.text and element.tail is not None and contral char (\n\t\r)
        def has_printable_content(element):
            def check(content):
                if content is not None:
                    return content.isspace()
                else:
                    return True

            result = not all((check(element.text), check(element.tail)))
            return result

        # check element.tag is not script (javascript) or style (css)
        def has_printable_tag(element):
            result = element.tag not in ["script", "style"]
            return result

        printable_elements = (
            seq(elements)
            .filter(lambda element: has_printable_content(element))
            .filter(lambda element: has_printable_tag(element))
            .cache()
        )

        return printable_elements.to_list()

    @property
    @lru_cache()
    def printable_elements(self):
        elements = HTMLElementAnalyzer.get_printable_elements(self.elements)
        return elements

    @staticmethod
    def get_content_size(element):
        # content include element.text and element.tail
        def replace_control_chars(text):
            chars = str.maketrans("\n\t\r", "   ")
            text = text.translate(chars)
            return text

        contents = (
            seq(element.text, element.tail)
            .map(lambda content: content if content is not None else "")
            .map(lambda content: replace_control_chars(content))
            .cache()
        )

        size = contents.map(lambda content: len(content)).sum()
        return size

    @staticmethod
    def ngrams(sequence, n=2):
        grams = zip(*[sequence[i:] for i in range(n)])
        return list(grams)

    @property
    # @lru_cache()
    def content_importance_of_edges(self):

        # get length of element's text, tail and sum up
        total_content_size = (
            seq(self.printable_elements)
            .map(lambda element: HTMLElementAnalyzer.get_content_size(element))
            .sum()
        )

        # count edges importance by it's content length (element.text, element.tail)
        content_importance_of_edges = (
            seq(self.printable_elements)
            .map(
                lambda element: (
                    [element] + list(element.iterancestors()),  # tree's branch
                    HTMLElementAnalyzer.get_content_size(element),  # get length
                )
            )
            .starmap(
                lambda nodes, content_size: (
                    HTMLElementAnalyzer.ngrams(nodes),
                    content_size,
                )
            )
            .starmap(
                lambda edges, content_size: seq(edges).starmap(
                    lambda dest, src: (
                        (src, dest),
                        content_size,
                    )  # reverse source, destiantion node. then pairing with size
                )
            )
            .flatten()
            .reduce_by_key(add)  # sum up the content size of edge
            .starmap(
                lambda edge, content_size: (edge, content_size / total_content_size)
            )
            .cache()
        )

        return content_importance_of_edges.to_list()

    @property
    # @lru_cache()
    def betweenness_centrality_of_nodes(self):
        # get edges
        edges = (
            seq(self.content_importance_of_edges)
            .starmap(lambda edge, content_importance: edge)
            .cache()
        )

        # build graph
        Tree = nx.Graph()
        Tree.add_edges_from(edges.to_list())

        betweenness_centrality_of_nodes = seq(
            nx.betweenness_centrality(Tree).items()
        ).cache()

        return betweenness_centrality_of_nodes.to_list()

    @property
    # @lru_cache()
    def importance_of_printable_elements(self):
        importance_of_printable_elements = (
            seq(self.content_importance_of_edges)
            .starmap(
                lambda edge, importance: (
                    edge[0],
                    importance,
                )  # get src node as key, and join with centrality
            )
            .join(self.betweenness_centrality_of_nodes)
            .starmap(
                lambda element, importance_centrality: (
                    element,
                    mul(
                        *importance_centrality
                    ),  # content_importance * betweenness_centrality
                )
            )
            .cache()
        )

        return importance_of_printable_elements.to_list()

    @staticmethod
    def get_xpath(element):
        xpath = element.getroottree().getpath(element)
        return xpath

    @property
    # @lru_cache()
    def primary_subtree_root(self):
        # get root of subtree by its importance (content_importance * betweenness_centrality)
        sorted_elements_by_importance = (
            seq(self.importance_of_printable_elements)
            .sorted(lambda row: row[1], reverse=True)
            .starmap(lambda element, importance: element)
            .to_list()
        )
        subtree_root = sorted_elements_by_importance[0]
        return subtree_root

    @property
    @lru_cache()
    def primary_subtree_leafs(self):
        root_xpath = HTMLElementAnalyzer.get_xpath(self.primary_subtree_root)
        elements = self.root.xpath(root_xpath + "//*")
        printable_leafs = HTMLElementAnalyzer.get_printable_elements(elements)
        return printable_leafs  # printable_leafs is list of content elements

    """
    pre-parsing
    maybe make a new class
    """

    @property
    @lru_cache()
    def keywords(self):
        """
        extract keyword with gensim keywords function,
        it needs to rewrite this discontinued parts in the future

        warning message:
        DeprecationWarning: `scipy.sparse.sparsetools` is deprecated!
        scipy.sparse.sparsetools is a private module for scipy.sparse,
        and should not be used.
        """

        # extract printable texts
        corpus = (
            seq(self.primary_subtree_leafs)
            .filter(lambda element: element.tag not in ["pre", "code"])
            .filter(lambda element: type(element.text) == str)
            .map(lambda element: element.text)
            .make_string(" ")
        )

        words = keywords(
            corpus,
            ratio=0.01,
            split=True,
            # scores=True,
            pos_filter=["NN", "JJ"],
            lemmatize=True,
            deacc=True,
        )
        return words

    @property
    @lru_cache()
    def title(self):
        title = (
            seq(self.elements)
            .filter(lambda element: element.tag == "h1")
            .map(lambda element: element.text)
            .make_string(" ")
        )
        return title

    @property
    @lru_cache()
    def created_time(self):
        # refactor maybe
        time = (
            seq(self.elements)
            .filter(lambda element: element.tag == "time")
            .map(lambda element: element.attrib.get("datetime"))
            .take(1)
            .make_string(" ")
        )
        return time
