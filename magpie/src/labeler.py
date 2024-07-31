"""
label match
"""

from enum import Enum
from collections import ChainMap
# from collections.abc import Mapping
from itertools import product
from functools import lru_cache
from functional import seq
from textdistance import jaro
from .label import PulseLabelGenerator, IndicatorLabelGenerator

class MatchThreshold(Enum):
    """
    label matching threshold for different method
    """
    exactly_match = 1
    fuzzy_match = 0.9

class FeedLabeler:

    """
    generate labeler from alienvault feed
    """

    PULSE = [
        "name",  # pulse.name
        "description",  # pulse.description
        "adversary",  # pulse.adversary
        "tags",  # pulse.tags
        "targeted_countries",  # pulse.targeted_countries
        "malware_families",  # pulse.malware_families
        "attack_ids",  # pulse.attack_ids
        "industries",  # pulse.industries
    ]

    def __init__(self, feed):
        self.feed = feed

    @property
    def pulse_label(self):
        """
        select pulse field's name and value, and generate label
        """
        pulse = {key: self.feed.get(key) for key in self.PULSE}
        label_processor = PulseLabelGenerator(pulse)
        return label_processor.get_label()

    @property
    def indicator_label(self):
        """
        select indicators field's name and value, and generate label
        """
        indicators = self.feed.get("indicators")
        label_processor = IndicatorLabelGenerator(indicators)
        return label_processor.get_label()

    @property
    @lru_cache()
    def label(self):
        """
        aggregate pulse and indicator label
        """
        return ChainMap(self.pulse_label, self.indicator_label)

    def match_label(self, string, method="fuzzy_match"):
        """
        get string's label with fuzzy match
        """
        matchings = (
            seq(self.label.items())
            .starmap(lambda k, v: (jaro.normalized_similarity(k, string), v))
            .filter(
                lambda similar_string: similar_string[0]
                >= MatchThreshold[method].value
            )
            .sorted(lambda similar_string: similar_string[0], reverse=True)
            .cache()
        )

        if matchings.empty():
            label = None
        else:
            label = matchings.starmap(lambda similarity, label: label).first()

        return label


class ElementLabeler:

    """
    element labeler html text formatting, such as
    <p>
        "Game studio CD Projekt Red recently "
        <a href="...">
            disclosed
        </a>
        " that it became a victim of a targeted, highly-impactful ransomware.
    </p>
    """

    def __init__(self, printable_elements, content_extractor, entity_parser, feed_labeler):
        self.printable_elements = printable_elements
        self.content_extractor = content_extractor
        self.entity_parser = entity_parser
        self.feed_labeler = feed_labeler

    @property
    def formattingtext_families(self):
        """
        get text formatting element and it's context elements
        """
        # get ancestor elements which has descendants one in printable elements
        ancestors = seq(self.printable_elements).filter(
            lambda element: seq(element.iterdescendants()).intersection(
                self.printable_elements
            )
        )
        # conbine ancestor element and descendant element
        families = ancestors.map(
            lambda element: [element] + list(element.iterdescendants())
        )
        return families


    def extract_text(self, elements):
        """
        extract text with "content_extractor" and "entity_parser"
        """
        product_by_contents = lambda element: product(
            [element], self.content_extractor.get_contents(element)
        )

        product_by_entities = lambda element, content: product(
            [element], [content], self.entity_parser.iterscan(content)
        )

        text = (
            seq(elements)
            .map(product_by_contents)
            .flatten()
            .starmap(product_by_entities)
            .flatten()
            .starmap(lambda element, content, text: text.string)
            .make_string(" ")
        )

        return text

    @property
    @lru_cache()
    def label(self):
        """
        list all element and context ones, then generate label
        """
        label = (
            self.formattingtext_families.map(
                lambda elements: (elements, self.extract_text(elements))
            )
            .starmap(lambda elements, string: product(elements, [string]))
            .flatten()
            .starmap(
                lambda element, string: (
                    element,
                    self.feed_labeler.match_label(string, method="fuzzy_match"),
                )
            )
            .filter(lambda element_label: element_label[1] is not None)
        )

        return label.to_dict()

    def match_label(self, element):
        """
        get label for context text formatting element
        """
        return self.label.get(element)
